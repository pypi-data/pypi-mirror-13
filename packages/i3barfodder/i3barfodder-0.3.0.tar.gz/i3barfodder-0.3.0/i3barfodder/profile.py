# Released under GPL3 terms (see LICENSE)

import os
import time
import functools
import inspect
import sys

def log(msg):
    print(msg, file=sys.stderr, flush=True)

class profile():
    """Decorator that prints to STDERR how much time was spent in a function"""
    def __init__(self, report_interval=5):
        self._times = []
        self._callers = {}
        self._last_report = time.time()
        self._report_interval = report_interval

    def __call__(self, func):
        self._funcname = format(func.__qualname__)
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            caller = inspect.stack()[2][3]
            if caller not in self._callers:
                self._callers[caller] = 0
            self._callers[caller] += 1

            start = time.time()
            result = func(*args, **kwargs)
            stop = time.time()
            self._times.append((stop - start) * 1e6)
            if stop - self._last_report > self._report_interval:
                self.report()
            return result
        return wrapped

    def report(self):
        since_last_report = time.time() - self._last_report
        cumtime = sum(self._times)
        percalltime = cumtime / len(self._times)
        persectime = cumtime / since_last_report
        log('{:3d} calls; {:.1f}µs/call; {:.0f}µs/second: {}'
                .format(len(self._times), percalltime, persectime, self._funcname))
        log('  {} callers: {}'.format(self._funcname, self._callers))

        self._times = []
        self._callers = {}
        self._last_report = time.time()


import cProfile, pstats
from io import StringIO

class subprofile():
    """Decorator that prints cProfile information to STDERR"""
    def __init__(self, report_interval=3, sortby='cumtime'):
        self._sortby = sortby
        self._last_report = time.time()
        self._report_interval = report_interval
        self._profiler = cProfile.Profile()

    def __call__(self, func):
        self._funcname = format(func.__qualname__)
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            self._profiler.enable()
            result = func(*args, **kwargs)
            self._profiler.disable()
            if time.time() - self._last_report > self._report_interval:
                self.report()
            return result
        return wrapped

    def report(self):
        s = StringIO()
        ps = pstats.Stats(self._profiler, stream=s).sort_stats(self._sortby)
        ps.print_stats(10)  # Show top 10
        log(s.getvalue())

        self._last_report = time.time()
        self._profiler = cProfile.Profile()
