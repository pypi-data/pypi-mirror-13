# Released under GPL3 terms (see LICENSE)

"""Provide information about the CPU"""

from i3bfutils import (io, rate)
psutil = io.import_or_croak('psutil')


# Number of cores
CORECOUNT = psutil.cpu_count()

# Overall cpu usage
_overall = None
def usage(samples=1):
    """Return overall CPU usage in percent

    `samples` is the number of previous values used to compute an average.
    """
    global _overall
    if _overall is None:
        _overall = rate.Average(samples)
    return _overall.update(psutil.cpu_percent())


# Usage per core
_cores = None
def usage_per_core(samples=1):
    """Return CPU core usage as a tuple of percentages

    `samples` is the number of previous values used to compute an average.
    """
    global _cores
    if _cores is None:
        _cores = [rate.Average(samples) for _ in range(CORECOUNT)]
    for corenum,percent in enumerate(psutil.cpu_percent(percpu=True)):
        _cores[corenum].update(percent)
    return tuple(float(core) for core in _cores)


# Ignore first cpu_percent() return value as the documentation suggests
psutil.cpu_percent()
