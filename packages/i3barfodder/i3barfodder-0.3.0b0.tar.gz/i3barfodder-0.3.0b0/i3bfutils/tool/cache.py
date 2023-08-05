# Released under GPL3 terms (see LICENSE)

"""Caching tools"""

from . import io
import functools
import time
import datetime

class timeout():
    """
    Cache return values for `seconds` before calling the function again.

    If `each` is specified, it must be one of 'second', 'minute', 'hour',
    'day', 'month', 'year' or 'eternity' and the decorated function's return
    value is deprecated at the start of each second, minute, hour, etc.

    The arguments passed to the decorated function are used as a unique call
    ID. Subsequent calls with the same arguments return the return value of
    the previous call.

    NOTE: Handling the cache and calculating timeouts adds relevant
    overhead. Be sure to check whether using this decorator actually increases
    efficiency.

    """
    def __init__(self, seconds=0, each=''):
        self._max_age = max(0, seconds)
        self._each = each
        self._returnvalues = {}
        self._timestamps = {}
        self._targets = {}

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            callid = tuple([args, frozenset(kwargs.items())])
            if self._timedout(callid):
                self._returnvalues[callid] = func(*args, **kwargs)
                self._timestamps[callid] = time.time()
                self._set_next_target(callid)
            return self._returnvalues[callid]

        def clearcache():
            self._returnvalues = {}
            self._timestamps = {}

        wrapped.clearcache = clearcache
        return wrapped

    def _timedout(self, callid):
        if callid in self._targets:
            target = self._targets[callid]
            if target is None:
                return False  # Return value of the first call is eternal
            else:
                return time.time() - self._targets[callid] >= 0
        else:
            return True  # First call

    def _set_next_target(self, callid):
        if self._max_age == 0 and self._each == '':
            self._targets[callid] = 0  # No timeout specified

        if callid not in self._timestamps:
            self._targets[callid] = 0  # First call

        if self._max_age != 0:
            # Next call in max age of each call
            self._targets[callid] = self._timestamps[callid] + self._max_age

        if self._each != '':
            # Next call at the start of the next second/minute/hour/etc
            last_call = datetime.datetime.fromtimestamp(self._timestamps[callid])
            if self._each == 'second':
                target = last_call + datetime.timedelta(seconds=1)
                target -= datetime.timedelta(microseconds=last_call.microsecond)
            elif self._each == 'minute':
                target = (last_call + datetime.timedelta(minutes=1))
                target -= datetime.timedelta(microseconds=last_call.microsecond,
                                             seconds=last_call.second)
            elif self._each == 'hour':
                target = (last_call + datetime.timedelta(hours=1))
                target -= datetime.timedelta(microseconds=last_call.microsecond,
                                             seconds=last_call.second,
                                             minutes=last_call.minute)
            elif self._each == 'day':
                target = (last_call + datetime.timedelta(days=1))
                target -= datetime.timedelta(microseconds=last_call.microsecond,
                                             seconds=last_call.second,
                                             minutes=last_call.minute,
                                             hours=last_call.hour)
            elif self._each == 'month':
                this_month = last_call.month
                next_month = this_month+1 if this_month < 12 else 1
                target = datetime.datetime(last_call.year, next_month, 1)
            elif self._each == 'year':
                target = datetime.datetime(last_call.year+1, 1, 1)
            elif self._each == 'eternity':
                target = None
            else:
                raise ValueError('Invalid argument for `each`: {!r}'.format(self._each))

            self._targets[callid] = None if target is None else target.timestamp()
