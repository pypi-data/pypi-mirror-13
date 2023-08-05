# Released under GPL3 terms (see LICENSE)

"""Provide easy access to hardware sensors"""

# TODO: This should use pysensors, but it doesn't support python3 yet. Or does it?
# https://bitbucket.org/blackjack/pysensors/issues/1/python3-support

from i3bfutils import io

def get_temperature_from_sys(path):
    """Return temperature from /sys/ path, e.g. /sys/class/hwmon/hwmon1/device/temp1_input"""
    temp_str = io.read_file(path)
    # If temperature is >= 1000, assume millidegrees
    if len(temp_str) >= 4:
        temp_str = temp_str[:-3]
    try:
        return int(temp_str)
    except ValueError:
        io.croak('{}: Not a number: {}'.format(path, temp_str))
