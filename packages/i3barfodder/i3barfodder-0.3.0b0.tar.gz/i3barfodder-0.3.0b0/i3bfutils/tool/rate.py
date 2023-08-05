# Released under GPL3 terms (see LICENSE)

"""Tools to deal with rates (e.g. byterates)"""

from . import io
import time

class RatePerSecond():
    """Turn a growing number into a per second rate"""

    def __init__(self):
        self._prev_value = None
        self._prev_time = 0
        self._rate = 0

    def update(self, value):
        """Update rate with the growing number `value` and return the new rate"""
        try:
            diff = value - self._prev_value
        except TypeError:
            diff = 0
        now = time.time()
        self._rate = diff / (now - self._prev_time)
        self._prev_value = value
        self._prev_time = now
        return self._rate

    def __float__(self):
        return float(self._rate)

    def __int__(self):
        return int(self._rate)

    def __repr__(self):
        return str(int(self))


class Average():
    """Calculate average based on `samples` most recent samples"""

    def __init__(self, samples=1):
        self.samples = samples
        self._values = []

    def update(self, value):
        """Update average with `value` and return the new average"""
        self._values.append(value)
        while len(self._values) > self.samples:
            self._values.pop(0)
        return float(self)

    def __float__(self):
        return float(sum(self._values) / len(self._values))

    def __int__(self):
        return int(float(self))

    def __repr__(self):
        return str(int(self))

