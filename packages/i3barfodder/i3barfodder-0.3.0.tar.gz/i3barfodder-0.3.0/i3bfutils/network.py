# Released under GPL3 terms (see LICENSE)

"""Provide information about network devices (needs psutil)"""

from i3bfutils import (io, rate, cache)
import subprocess
import shlex
_psutil = io.import_or_croak('psutil')


_nic_rates = {}
_nic_rates_avg = {}

@cache.timeout(seconds=0.1)
def get_byterate(nic, direction, samples=1):
    """
    Return current byte throughput of network interface `nic`

    `nic` is the name of the network interface (e.g. 'eth0').

    `direction` must be 'up' or 'down'.

    `samples` is the number of previous values to compute the average.
    """
    counters = _psutil.net_io_counters(pernic=True)
    if nic not in counters:
        io.croak('Unknown NIC: {}'.format(nic))
    else:
        if nic not in _nic_rates:
            _nic_rates[nic] = { 'up': rate.RatePerSecond(),
                                'down': rate.RatePerSecond() }
            _nic_rates_avg[nic] = { 'up': rate.Average(samples),
                                    'down': rate.Average(samples) }

        if direction == 'down':
            current_value = counters[nic].bytes_recv
        elif direction == 'up':
            current_value = counters[nic].bytes_sent
        else:
            io.croak('Invalid direction: {!r}'.format(direction))

        rps = _nic_rates[nic][direction]
        avg = _nic_rates_avg[nic][direction]
        current_rate = rps.update(current_value)
        current_rate_avg = avg.update(current_rate)
        return int(current_rate_avg)


def get_default_nic():
    """Return the name of the default NIC according to 'ip route | grep ^default'"""
    cmd = 'ip route'
    try:
        lines = subprocess.check_output(shlex.split(cmd),
                                        universal_newlines=True).split('\n')
    except Exception as e:
        io.croak('Unable to auto-detect default NIC: '
                 'Running "{}" failed: {}'.format(cmd, e))

    for line in lines:
        if line.startswith('default'):
            try:
                start = line.index('dev ') + 4
            except ValueError:
                io.croak('No NIC found for default route: {}'.format(line))

            try:
                end = line[start:].index(' ') + start
            except ValueError:
                end = len(line)-1
            nic = line[start:end]
            io.debug('Auto-detected default NIC: {}'.format(nic))
            return nic

    io.croak('No default route in output of "ip route" found:\n' + \
             '\n'.join(lines))
