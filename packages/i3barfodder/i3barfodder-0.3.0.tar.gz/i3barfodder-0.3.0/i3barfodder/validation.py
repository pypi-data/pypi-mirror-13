# Released under GPL3 terms (see LICENSE file)

import os
import operator
import logging
from .util import str2num
from . import error


class VDict(dict):
    """Dictionary that validates keys and values"""

    def __init__(self, validators={}, valid_keys=None, *args, **kwargs):
        """
        `validators` is a dictionary that maps keys to validators. A validator
        is a callable that accept the value as a single argument and returns a
        valid value.

        `valid_keys` is an iterable of allowed keys. If unspecified, all keys
        are allowed. `error.InvalidKey` is raised if an invalid key is set.

        Any other arguments are forwarded to `update`.
        """
        super().__init__()
        self.valid_keys = valid_keys
        self.validators = validators
        self.update(**kwargs)

    def __setitem__(self, key, value):
        if self.valid_keys is not None and key not in self.valid_keys:
            raise error.InvalidKey(key)
        else:
            if key in self.validators:
                value = self.validators[key](value)
            dict.__setitem__(self, key, value)

    def update(self, dct={}, **kwargs):
        if not isinstance(dct, dict):
            dct = dict(dct)   # Convert tuples, generator, etc to dict
        else:
            dct = dct.copy()  # Don't modify caller's dct
        if kwargs:
            dct.update(**kwargs)
        for k,v in dct.items():
            self[k] = v


def validate_number(val, min=None, max=None, silent=False):
    """
    Validate and return float and int

    `min` and `max` set the allowed limits.

    If `silent` is True, limits are enforced silently by returning the
    min/max limit instead of the value.

    Valid unit prefixes are T/Ti, G/Gi, M/Mi and k/Ki. Case is ignored.

    Raise `error.InvalidValue` if validation fails.
    """
    val = str2num(val)
    # Check min/max limits
    if min is not None:
        min = str2num(min)
        if val < min:
            if silent:
                return min
            else:
                raise error.InvalidValue('{!r} is too small'.format(val))

    if max is not None:
        max = str2num(max)
        if val > max:
            if silent:
                return max
            else:
                raise error.InvalidValue('{!r} is too big'.format(val))
    return val


def validate_integer(val, min=None, max=None, silent=False):
    """
    Validate and return int only

    If `silent` is False, floats raise `error.InvalidValue`, otherwise they
    are rounded.

    See `validate_number` for more information.
    """
    val = validate_number(val, min, max, silent)
    if not isinstance(val, int):
        if silent:
            return round(val)
        else:
            raise error.InvalidValue('{!r} is not an integer'.format(val))
    return val


TRUES = 'true 1 on yes'.split()
FALSES = 'false 0 off no'.split()
_TRUES_AND_FALSES = ', '.join(('/'.join(pair) for pair in zip(TRUES, FALSES)))
def validate_bool(val):
    """
    Validate and return boolean values case-insensitively

    True values are: true 1 on yes
    False values are: false 0 off no

    Raise `error.InvalidValue` if validation fails.
    """
    if str(val).lower() in TRUES:
        return True
    if str(val).lower() in FALSES:
        return False
    raise error.InvalidValue('{!r} must be one of: {}'.format(val, _TRUES_AND_FALSES))


def validate_option(val, options):
    """Return `v` if part of `options` or raise `error.InvalidValue`"""
    if val not in options:
        raise error.InvalidValue('{!r} must be one of: {}'
                                 .format(val, ', '.join(options)))
    return val


def validate_list(val):
    """If `val` is a list, tuple or set, return it as a list or raise `error.InvalidValue`"""
    if not isinstance(val, (list, tuple, set)):
        raise error.InvalidValue('{!r} must be a list'.format(val))
    return list(val)


def validate_path(path):
    """Return `path` with '~' expanded to $HOME"""
    return os.path.expanduser(path)


def validate_PATH(path):
    """
    Append `path` to the value of the environment variable `PATH` and return it

    User HOME expansion is applied with `validate_path`.
    """
    if path != '':
        path = os.pathsep.join((os.environ['PATH'], validate_path(path)))
    return path
