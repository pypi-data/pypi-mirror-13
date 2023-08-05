# Released under GPL3 terms (see LICENSE)

"""Provide information about new packages"""

from i3bfutils.tool import (io, inotify)
import os
import subprocess
import time
import asyncio
import locale
locale.setlocale(locale.LC_ALL, '')


# All package manager classes should inherit from _pkgmgr so NAMES at the end
# of this file can keep a list of all supported package managers.
class _pkgmgr():

    def wait_for_cache_update(self):
        """Block until the number of available packages has changed"""
        raise NotImplementedError

    def wait_for_cache_update_async(self, callback, loop=None):
        """Run `callback` whenever the number of available packages may have changed"""
        raise NotImplementedError

    def count_new_packages(self):
        """Return the number of packages available for installation"""
        raise NotImplementedError


class apt(_pkgmgr):
    # TODO: Using python3-apt might be a better way to count new packages, and
    # 'dist-upgrade' probably doesn't work on stable.

    # Also, using inotify on the cache file isn't very precise (cache is
    # written multiple times and doesn't always exist), but I can't think of a
    # better way and it seems to work.

    _CACHE_FILE = '/var/cache/apt/pkgcache.bin'
    _COUNT_CMD = ('nice -19 apt-get dist-upgrade --simulate | grep "^Inst " | wc --lines')
    _INOTIFY_EVENTS = ('close_write', 'delete_self')

    def __init__(self):
        self._prev_cache_update = 0

    def _assert_cache_file_exists(self):
        # Cache file does not always exist, but it should appear eventually.
        tries = 0
        max_tries = 10
        while not os.path.exists(self._CACHE_FILE):
            time.sleep(1)
            tries += 1
            if tries >= max_tries:
                io.croak('Cache file doesn\'t exist: {!r}'.format(self._CACHE_FILE))

    def wait_for_cache_update(self):
        """Block until the number of available packages has changed"""
        self._assert_cache_file_exists()
        inotify.wait(self._CACHE_FILE, events=self._INOTIFY_EVENTS)

        # Ignore changing cache if it changed recently
        now = time.time()
        if now - self._prev_cache_update < 10:
            self.wait_for_cache_update()
        self._prev_cache_update = now

    def wait_for_cache_update_async(self, callback, loop=None):
        """Run `callback` whenever the number of available packages may have changed"""

        loop = loop if loop is not None else asyncio.get_event_loop()

        # The cache file gets deleted during the update, so we have to detect
        # that, wait for the new cache file to appear, and then set a new
        # watch.  callback_wrapper gets called with an IN_IGNORED event (I
        # don't know why, though) after the new watch is created which should
        # run the callback as soon as the new cache file appears.  Hopefully
        # pyinotify removes the dead watch for the old file on its own.

        def callback_wrapper(event):
            if event.maskname == 'IN_DELETE_SELF':
                start_watching()
            else:
                callback()

        def start_watching():
            self._assert_cache_file_exists()
            inotify.wait_async(self._CACHE_FILE, callback=callback_wrapper,
                               events=self._INOTIFY_EVENTS, loop=loop)

        start_watching()

    def count_new_packages(self):
        """Return the number of packages available for installation"""
        fail_msg = 'Counting new packages failed: '
        try:
            num = subprocess.check_output(self._COUNT_CMD,
                                          shell=True,
                                          universal_newlines=True).strip()
        except Exception as e:
            io.croak(fail_msg + str(e))
        else:
            try:
                num = int(num)
            except ValueError:
                io.croak(fail_msg + '{!r} returned {!r}'.format(self._COUNT_CMD, num))
            else:
                return num


# List of classes that derived from _pkgmgr
NAMES = tuple(local.__name__ for local in locals().values()
              if type(local) is type and _pkgmgr in local.mro() \
              and local.__name__[0] != '_')
