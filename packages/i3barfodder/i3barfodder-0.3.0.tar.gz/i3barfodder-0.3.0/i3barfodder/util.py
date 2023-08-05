# Released under GPL3 terms (see LICENSE file)
import re
import math
from . import error

class Ratio():
    """Relation of a changing number to minimum and maximum numbers"""

    SCALES = { 'linear': lambda v: v,
               'sqrt': math.sqrt,
               'log': math.log }

    def __init__(self, *settings):
        self._ratio = None
        self._value = None
        self._min = 0
        self._max = 0
        self.min_is_soft = True
        self.max_is_soft = True
        self._scalename = 'linear'
        self._scale = self.SCALES[self._scalename]
        self._recalc = True
        self.update(*settings)
        if self._value is None: self._value = self._min
        if self._ratio is None: self._ratio = float(0)

    def update(self, *settings):
        for k,v in settings:
            self[k] = v

    def __getitem__(self, item):
        if item == 'value': return self._value
        if item in ('min', 'softmin'): return self._min
        if item in ('max', 'softmax'): return self._max
        if item == 'scale': return self._scalename
        raise error.InvalidKey(item)

    def __setitem__(self, item, value):
        if item in ('value', 'min', 'max', 'softmin', 'softmax'):
            value = str2num(value)
        else:
            value = str(value)

        if item == 'value':
            if value < self._min:
                if self.min_is_soft:
                    self['softmin'] = value
                else:
                    value = self._min
            elif value > self._max:
                if self.max_is_soft:
                    self['softmax'] = value
                else:
                    value = self._max
            self._value = value

        elif item == 'min':
            self._min = value
            self.min_is_soft = False
        elif item == 'max':
            self._max = value
            self.max_is_soft = False

        elif item == 'softmin':
            self._min = value
            self.min_is_soft = True
        elif item == 'softmax':
            self._max = value
            self.max_is_soft = True

        elif item == 'scale':
            value = value.lower()
            if value not in self.SCALES:
                raise error.InvalidValue('Invalid scale: {!r}'.format(value))
            else:
                self._scale = self.SCALES[value]
                self._scalename = value
        else:
            raise error.InvalidKey(item)

        self._recalc = True

    def __float__(self):
        """Return ratio as float between 0 and 1"""
        if self._recalc:
            abs_max = self._max - self._min
            abs_rel = self._value - self._min
            try:
                abs_max = self._scale(abs_max)
                abs_rel = self._scale(abs_rel)
            except ValueError:
                pass  # Ignoring 'math domain error' seems to work

            try:
                self._ratio = float(max(0, min(1, abs_rel/abs_max)))
            except ZeroDivisionError:
                self._ratio = float(0)

            self._recalc = False

        return self._ratio

    def __round__(self, n=0):
        return round(float(self), n)

    def __str__(self):
        return str(round(self, 3))

    @property
    def as_percent(self):
        return float(self) * 100

    def copy(self):
        settings = [('value', self._value), ('scale', self._scalename)]
        if self.min_is_soft:
            settings.append(('softmin', self._min))
        else:
            settings.append(('min', self._min))
        if self.max_is_soft:
            settings.append(('softmax', self._max))
        else:
            settings.append(('max', self._max))
        return type(self)(*settings)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            for key in ('value', 'min', 'max', 'scale'):
                if self[key] != other[key]:
                    return False
            for attr in ('min_is_soft', 'max_is_soft', '_ratio'):
                if getattr(self, attr) != getattr(other, attr):
                    return False
            return True
        elif isinstance(other, (int, float)):
            return self._ratio == other
        else:
            return NotImplemented

    def __repr__(self):
        r = '<{} {}->{}'.format(type(self).__name__, self._value, self._ratio)
        if self.min_is_soft:
            r += ', softmin={}'.format(self._min)
        else:
            r += ', min={}'.format(self._min)
        if self.max_is_soft:
            r += ', softmax={}'.format(self._max)
        else:
            r += ', max={}'.format(self._max)
        r += ', scale={}>'.format(self._scalename)
        return r


_UNIT_PREFIXES = (
    ('ki', 1024), ('mi', 1024**2), ('gi', 1024**3), ('ti', 1024**4), ('pi', 1024**5),
    ('k',  1000), ('m',  1000**2), ('g',  1000**3), ('t',  1000**4), ('p',  1000**5),
)

def str2num(val, strict=True):
    """
    Convert human-readable number to integer or float

    Valid unit prefixes are k/M/G/T/P for multiples of 1000 and Ki/Mi/Gi/Ti/Pi
    for multiples of 1024. Everything after the unit prefix is ignored.

    If `strict` is False, any string that can't be converted to a number is
    returned unchanged.

    >>> str2num('1k')
    1000
    >>> str2num('1 Ki')
    1024
    >>> str2num('4.3 Gi')
    4617089843.2

    It's also possible to calculate a fraction of a number with a percentage:

    >>> str2num('10%37')
    3.7
    >>> str2num('1%2.5')
    0.025
    >>> str2num('200%5k')
    10000
    """
    if isinstance(val, str):
        if val == 'inf':
            return float('inf')

        # 'X%Y' -> return X percent of Y
        if '%' in val:
            v1, v2 = (str2num(val, strict) for val in val.split('%', 1))
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                num = v2*v1/100
            else:
                num = val

        else:
            # Find unit prefix. Everything left of it is the number; everything
            # right of it is a unit (e.g. 'B/s') and irrelevant here.
            num = val.lower()
            for prefix,size in _UNIT_PREFIXES:
                prefix = prefix
                if prefix in num:
                    prefix_pos = num.index(prefix)
                    num = num[:prefix_pos].rstrip()
                    try:
                        num = float(num) * size
                    except ValueError:
                        pass
                    else:
                        break

            # Number has no known unit prefix
            if not isinstance(num, float):
                try:
                    num = float(num)
                except ValueError:
                    pass
    else:
        num = val

    if not isinstance(num, (int, float)):
        if strict:
            raise error.InvalidValue('{!r} is not a number'.format(val))
        else:
            return val
    else:
        if num != float('inf'):
            # Float if necessary, int otherwise
            num_float = float(num)
            num_int = int(num_float)
            num = num_int if num_int == num_float else num_float

    return num


def parse_params(paramstr):
    """
    Parse parameters pairs of the format P1:P2:P3:...

    Parameters are split and returned as two tuples:

    - The first tuple contains all positional parameters, i.e. parameters that
      don't contain '='.

    - The second tuple contains all keyword parameters as (key, value) tuples.

    Values are converted to `int` or `float`, if possible, with `str2num`.
    """
    pos = []
    kw = []
    for arg in paramstr.split(':'):
        try:
            key,value = arg.split('=', 1)
        except ValueError:
            key,value = (None, arg)
        value = str2num(value, strict=False)
        if key is None:
            pos.append(value)
        else:
            kw.append((key,value))
    return (tuple(pos), tuple(kw))


def parse_args(argstr):
    """
    Parse function argument string with positional and keyword arguments

    Numbers are converted to `int` or `float`, if possible.

    Returns a tuple of positional arguments and a tuple of (key,value) tuples.
    """
    if argstr == '':
        return ((), ())
    else:
        posargs = []
        kwargs = []
        for arg in (arg.strip() for arg in argstr.split(',')):
            if '=' in arg:
                key,value = (x.strip() for x in arg.split('=', 1))
                kwargs.append((key, str2num(value, strict=False)))
            else:
                posargs.append(str2num(arg, strict=False))
        return (tuple(posargs), tuple(kwargs))


def pos2kwargs(posargs, kwargs, keys):
    """zip() `posargs` with `keys` into a mapping and combine it with mapping `kwargs`

    Raises `error.Argument` if any key is in `kwargs`.
    """
    combined_args = []
    kwarg_dct = dict(kwargs)
    for key,value in zip(keys, posargs):
        if key in kwarg_dct:
            raise error.Argument("{0!r} given twice: '{1}', '{0}={2}'"
                                 .format(key, value, kwarg_dct[key]))
        else:
            combined_args.append((key, value))
    return tuple(combined_args) + tuple(kwargs)


def parse_function_calls(text, function_names, function_caller):
    results = []
    offset = 0
    for fncall in find_function_calls(text, function_names):
        result = function_caller(fncall['func'], fncall['id'], fncall['argstr'])
        start = fncall['start'] - offset
        end = fncall['end'] - offset
        text = text[:start] + result + text[end:]
        offset += fncall['len'] - len(result)
    return text


_FUNC_REGEXES = {}
def find_function_calls(text, funcnames):
    funcnames = tuple(sorted(funcnames, key=lambda fn: len(fn), reverse=True))
    if funcnames in _FUNC_REGEXES:
        func_regex = _FUNC_REGEXES[funcnames]
    else:
        func_regex = re.compile(r'(?P<func>' + r'|'.join(funcnames) +
                                r')(?P<id>\S*?)\((?P<args>.*?)\)')
        _FUNC_REGEXES[funcnames] = func_regex

    for match in func_regex.finditer(text):
        yield { 'func': match.group('func'),
                'id': match.group('id'),
                'argstr': match.group('args'),
                'len': len(match.group(0)),
                'start': match.start(),
                'end': match.end() }
