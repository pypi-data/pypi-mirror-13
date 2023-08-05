# Released under GPL3 terms (see LICENSE)

"""Special sleep functions"""

from . import io
import time
from datetime import (datetime, timedelta)
import select
import sys
import json
import asyncio


def target_second(delay):
    """Adjust `delay` so that it targets the start of the second"""
    now = time.time()
    return int(now) + delay - now


def sleep(seconds):
    """
    Sleep for int(time.time()) + `seconds`

    This is useful to:

    - synchronize different processes (within a few milliseconds),
    - prevent skipping seconds due to processing overhead,
    - display the time precisely.

    Instead of sleeping, for example, 1 second, sleep until the next second
    starts.  With a simple time.sleep(1), this happens::

        10:30:15.997
      +        1.000s # sleep(1)
      +        0.005s # time to run time.strftime()
      = 10:30:17.002  # Where's 10:30:16?
    """
    time.sleep(target_second(seconds))


def sleep_til_midnight():
    """Sleep until the next day starts"""
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    secs_till_midnight = (midnight - now).total_seconds()
    # io.debug('Sleeping {} seconds from {} until midnight at {}'
    #          .format(secs_till_midnight, now.timestamp(), midnight.timestamp()))
    time.sleep(secs_till_midnight)


def wait_for_click(timeout=None):
    """
    Sleep until a click event is received on stdin

    If `timeout` is not None, wait no longer than that many seconds.

    Returns None if timeout occured, or a dictionary according to the i3bar
    protocol: https://i3wm.org/docs/i3bar-protocol.html#_click_events
    """
    if timeout is None:
        rlist, _, _ = select.select((sys.stdin,), (), ())
    else:
        timeout = target_second(timeout)
        rlist, _, _ = select.select((sys.stdin,), (), (), timeout)

    if sys.stdin in rlist:
        line = sys.stdin.readline().rstrip('\n')
        try:
            click = json.loads(line)
        except ValueError:
            io.debug('Invalid click event: {!r}'.format(line))
        else:
            return click


def wait_for_click_async(callback, loop=None):
    """
    Same as `wait_for_click` but using asyncio

    >>> def handle_click(click):
    >>>    print('Received click event: {}'.format(click))
    >>> wait_for_click_async(handle_click)
    >>> asyncio.get_event_loop().run_forever()
    """
    loop = loop if loop is not None else asyncio.get_event_loop()

    def read_input():
        line = sys.stdin.readline().rstrip('\n')
        try:
            click = json.loads(line)
        except ValueError:
            io.debug('Invalid click event: {!r}'.format(line))
        else:
            callback(click)

    loop.add_reader(sys.stdin, read_input)
