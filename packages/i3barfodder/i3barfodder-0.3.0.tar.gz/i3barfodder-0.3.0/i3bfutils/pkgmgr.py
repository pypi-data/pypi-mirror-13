# Released under GPL3 terms (see LICENSE)

"""Provide information about new packages"""

from i3bfutils import (io, inotify)
import os
import asyncio
import locale
locale.setlocale(locale.LC_ALL, '')


# All package manager classes should inherit from pkgmgr so NAMES at the end
# of this file can keep a list of all supported package managers.
class pkgmgr():
    """
    Base class for package manager interfaces

    Classes derived from this class must implement the methods `on_change`,
    `on_change_async` and the property `new_package_count`.
    """
    pass


class apt(pkgmgr):
    """APT package manager (derivatives of Debian/Ubuntu/etc)"""

    _CACHE_FILE = '/var/cache/apt/pkgcache.bin'
    _cache = io.import_or_croak('apt').Cache()

    @property
    def new_package_count(self):
        """Number of updatable+new packages"""
        self._cache.open()
        self._cache.upgrade(dist_upgrade=True)
        io.debug('Package counters: broken={} remove={} install={} keep={}'
                 .format(self._cache.broken_count, self._cache.delete_count,
                         self._cache.install_count, self._cache.keep_count))
        return self._cache.install_count

    def on_cache_change(self, callback):
        """Call `callback` with `new_package_count` after package chache updates"""
        def handle_event(event):
            if event.name == os.path.basename(self._CACHE_FILE):
                callback(self.new_package_count)

        inotify.loop((os.path.dirname(self._CACHE_FILE),),
                     callback=handle_event,
                     events=('moved_to',))

    def on_cache_change_async(self, callback, loop=None):
        """Same as `on_cache_change` but using `inotify.loop_async` (asyncio)"""
        def handle_event(event):
            if event.name == os.path.basename(self._CACHE_FILE):
                callback(self.new_package_count)

        loop = loop if loop is not None else asyncio.get_event_loop()
        inotify.loop_async((os.path.dirname(self._CACHE_FILE),),
                           callback=handle_event,
                           events=('moved_to',))


# List of classes that derived from pkgmgr
NAMES = tuple(local.__name__ for local in locals().values()
              if type(local) is type and pkgmgr in local.mro() \
              and local.__name__[0] != '_')

_PKGMGRS = dict((name,globals()[name]) for name in NAMES)

def get(name):
    """Return package manager instance """
    try:
        return _PKGMGRS[name.lower()]()
    except KeyError:
        io.croak('Unknown package manager: {!r}\n'
                 'Available options are: {}'.format(name, ', '.join(NAMES)))
