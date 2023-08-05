# Released under GPL3 terms (see LICENSE)

"""Provide information about storage devices (needs psutil)"""

from i3bfutils import (rate, cache, convert, io)
import os
from collections.abc import Mapping
psutil = io.import_or_croak('psutil')


class Bytes(int):
    @property
    def pretty(self):
        return convert.num2str(self, binary=False) + 'B'

class Byterate(Bytes):
    @property
    def pretty(self):
        return super().pretty + '/s'

class Percent(float):
    @property
    def pretty(self):
        return str(round(self)) + ' %'

class Path(str):
    def __new__(cls, path):
        return super().__new__(cls, os.path.realpath(os.path.expanduser(path)))

    def __init__(self, path):
        if path.startswith('/home/'):
            self.__tildified = '~' + path[6:]
        else:
            self.__tildified = path

    @property
    def pretty(self):
        return self.__tildified


@cache.timeout(seconds=0.5)
def _cached_io_counters(*args, **kwargs):
    return psutil.disk_io_counters(*args, **kwargs)

@cache.timeout(seconds=0.5)
def _cached_disk_partitions(*args, **kwargs):
    return psutil.disk_partitions(*args, **kwargs)


class Mountpoint(Mapping):
    """
    Provide information about a mountpoint as a mapping

    Available keys:  
      - General: path, devpath, devname, fs, mounted  
      - Usage: free, used, total, free%, used%  
      - IO rates: read, write, rw  

    The values returned by these keys are human-readable strings. Each key has
    a machine-readable version that starts with a leading '_'. For paths, the
    '_' variant resolves links.
    """

    _info_keys = ('path', 'devpath', 'devname', 'fs')
    _usage_keys = ('free', 'used', 'total', 'used%', 'free%')
    _io_keys = ('read', 'write', 'rw')
    _keys = _info_keys + _usage_keys + _io_keys + ('mounted',)
    _keys += tuple('_'+k for k in _keys)

    def __init__(self, path, iosamples=3):
        """
        `path` is the path to the mountpoint.
        `iosamples` is the number of previous read/write/rw values that are
        used to compute an average.
        """
        self._info = { 'path': Path(path) }
        self._io_read = rate.RatePerSecond()
        self._io_write = rate.RatePerSecond()
        self._io_rw = rate.RatePerSecond()
        self._io_read_avg = rate.Average(samples=iosamples)
        self._io_write_avg = rate.Average(samples=iosamples)
        self._io_rw_avg = rate.Average(samples=iosamples)

    @property
    @cache.timeout(seconds=0.5)
    def info(self):
        """Return a dictionary with keys: path, devpath, devname, fs, mounted"""
        for partition in _cached_disk_partitions(all=False):
            if partition.mountpoint == self._info['path'].pretty:
                self._info['devpath'] = Path(partition.device)
                self._info['devname'] = os.path.basename(self._info['devpath'])
                self._info['fs'] = partition.fstype
                self._info['mounted'] = True
                return self._info
        self._info.update(devpath='', devname='', fs='', mounted=False)
        return self._info

    @property
    @cache.timeout(seconds=0.5)
    def usage(self):
        """Return a dictionary with keys: free, free%, used, used%, total"""
        if self.mounted:
            usage = psutil.disk_usage(self['_path'])
            return { 'free': Bytes(usage.free),
                     'used': Bytes(usage.used),
                     'total': Bytes(usage.total),
                     'used%': Percent(usage.percent),
                     'free%': Percent(100-usage.percent) }
        else:
            return { 'free': Bytes(0),
                     'used': Bytes(0),
                     'total': Bytes(0),
                     'used%': Percent(0),
                     'free%': Percent(0) }

    @property
    @cache.timeout(seconds=0.5)
    def io(self):
        """Return a dictionary with IO rates: read, write, rw"""
        if self.mounted:
            counters = _cached_io_counters(perdisk=True)[self['devname']]
            read_rate = self._io_read.update(counters.read_bytes)
            write_rate = self._io_write.update(counters.write_bytes)
            rw_rate = self._io_rw.update(counters.read_bytes + counters.write_bytes)
            return { 'read': Byterate(self._io_read_avg.update(read_rate)),
                     'write': Byterate(self._io_write_avg.update(write_rate)),
                     'rw': Byterate(self._io_rw_avg.update(rw_rate)) }
        else:
            return { 'read': Byterate(self._io_read_avg.update(0)),
                     'write': Byterate(self._io_write_avg.update(0)),
                     'rw': Byterate(self._io_rw_avg.update(0)) }

    @property
    def iosamples(self):
        return self._io_read_avg.samples
    @iosamples.setter
    def iosamples(self, samples):
        self._io_read_avg.samples = samples
        self._io_write_avg.samples = samples
        self._io_rw_avg.samples = samples

    @property
    def mounted(self):
        return self._info['devname'] is not ''

    def __getitem__(self, key):
        if key == 'mounted':
            return str(self.mounted).lower()
        elif key == '_mounted':
            return 1 if self.mounted else 0
        else:
            if key[0] == '_':
                func = lambda v: v
                key = key[1:]
            else:
                func = lambda v: v.pretty if hasattr(v, 'pretty') else str(v)

            if key in self._info_keys:
                return func(self.info[key])
            elif key in self._usage_keys:
                return func(self.usage[key])
            elif key in self._io_keys:
                return func(self.io[key])
            else:
                raise KeyError(key)

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        return iter(self._keys)

    def __lt__(self, other):
        if type(other) != type(self):
            return NotImplemented
        return self['path'] < other['path']

    def __eq__(self, other):
        if type(other) != type(self):
            return NotImplemented
        return self._info['path'] == other._info['path']

    def __hash__(self):
        return hash(self._info['path'])

    def __repr__(self):
        return '<{} {}>'.format(type(self).__name__, self._info['path'])


class Mountpoints(Mapping):
    """Auto-updated dictionary of mountpoints"""

    def __init__(self, blacklist=None, whitelist=None, permalist=None, iosamples=3,
                 on_added=(), on_removed=(), on_updated=()):
        self._mountpoints = {}
        self.iosamples = iosamples
        self._hooks = { 'added': list(on_added),
                        'removed': list(on_removed),
                        'updated': list(on_updated) }
        self._blacklist = ()
        self._whitelist = ()
        self._permalist = ()
        if blacklist is not None: self.blacklist = blacklist
        if whitelist is not None: self.whitelist = whitelist
        if permalist is not None: self.permalist = permalist

    @property
    def whitelist(self):
        """List of mountpoint paths to not ignore"""
        return self._whitelist
    @whitelist.setter
    def whitelist(self, lst):
        self._whitelist = tuple(set(os.path.normpath(path) for path in lst))
        self._is_wanted.clearcache()

    @property
    def blacklist(self):
        """List of mountpoint paths to ignore"""
        return self._blacklist
    @blacklist.setter
    def blacklist(self, lst):
        self._blacklist = tuple(set(os.path.normpath(path) for path in lst))
        self._is_wanted.clearcache()

    @property
    def permalist(self):
        """List of mountpoint paths to keep when unmounted"""
        return self._permalist
    @permalist.setter
    def permalist(self, lst):
        self._permalist = tuple(set(os.path.normpath(path) for path in lst))
        self._is_wanted.clearcache()

    @property
    def iosamples(self):
        """Number of samples to compute average IO rates"""
        return self._iosamples
    @iosamples.setter
    def iosamples(self, samples):
        self._iosamples = samples
        for mp in self._mountpoints:
            mp.iosamples = samples

    @cache.timeout(each='eternity')
    def _is_wanted(self, path):
        """Return whether `path` is part of `whitelist` or not part of `blacklist`"""
        def partof(lst, path):
            for lst_path in lst:
                if path == lst_path or \
                   lst_path[-1] == '*' and path.startswith(lst_path.rstrip('*').rstrip('/')):
                    return True
            return False

        if path in self.permalist:
            return True
        elif self.whitelist:
            # If whitelist is set, blacklist is ignored
            return partof(self.whitelist, path)
        else:
            return not partof(self.blacklist, path)

    def poll(self):
        """Add/Remove/Update mountpoints"""
        known_mps = self._mountpoints
        mp_paths = self.mountpoint_paths

        for path in mp_paths:
            if path not in known_mps:
                known_mps[path] = Mountpoint(path, iosamples=self._iosamples)
                self._run_hooks('added', known_mps[path])
            else:
                self._run_hooks('updated', known_mps[path])

        for path in tuple(known_mps):
            if path not in mp_paths:
                self._run_hooks('removed', known_mps[path])
                del(known_mps[path])

    @property
    def mountpoint_paths(self):
        """Existing mountpoints that are wanted according to `blacklist`, `whitelist` and `permalist`"""
        paths = tuple(part.mountpoint
                      for part in _cached_disk_partitions(all=False)
                      if self._is_wanted(part.mountpoint))
        if self._permalist:
            paths = tuple(set(paths).union(set(self._permalist)))
        return paths

    def on_added(self, callback):
        """Call `callback` with newly added mountpoint instance"""
        self._hooks['added'].append(callback)

    def on_removed(self, callback):
        """Call `callback` with newly removed mountpoint instance"""
        self._hooks['removed'].append(callback)

    def on_updated(self, callback):
        """Call `callback` with newly updated mountpoint instance"""
        self._hooks['updated'].append(callback)

    def _run_hooks(self, name, *args, **kwargs):
        for callback in self._hooks[name]:
            callback(*args, **kwargs)

    def __getitem__(self, item):
        self.poll()
        return self._mountpoints[item]

    def items(self):
        self.poll()
        return super().items()

    def __len__(self):
        self.poll()
        return len(self._mountpoints)

    def __iter__(self):
        self.poll()
        return iter(self._mountpoints)

    def __repr__(self):
        # self.poll()
        return repr(self._mountpoints)

    def __hash__(self):
        return id(self)
