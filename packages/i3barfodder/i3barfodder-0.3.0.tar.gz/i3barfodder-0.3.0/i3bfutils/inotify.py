# Released under GPL3 terms (see LICENSE)

"""Convenient pyinotify wrapper"""

from . import io
import asyncio
import os
pyinotify = io.import_or_croak('pyinotify')


def _make_event_mask(events):
    # Build event mask from event names
    eventmask = 0
    for eventname in events:
        try:
            event = getattr(pyinotify, 'IN_'+eventname.upper())
        except AttributeError as e:
            io.croak('Unknown event: {!r}'.format(eventname))
        else:
            eventmask |= event
    if eventmask == 0:
        eventmask = pyinotify.ALL_EVENTS
    return eventmask


def _make_watch_manager(paths, events=()):
    """Create `pynotify.WatchManager` instance

    `paths` is a sequence of paths to be watched.
    `events` is a sequence of event names.
    """
    eventmask = _make_event_mask(events)
    wm = pyinotify.WatchManager()
    for path in paths:
        try:
            # quiet=False actually means quiet=True, because it raises exceptions
            # instead of cluttering stderr
            wm.add_watch(path, eventmask, quiet=False)
        except pyinotify.WatchManagerError as e:
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            else:
                io.croak('Cannot watch {}: {}'.format(path, e))
        else:
            io.debug('Watching {} for: {}'.format(path, ', '.join(events)))
    return wm


def loop(paths, callback, events=()):
    """
    For each path in `paths` call `callback` with a `pyinotify.Event` instance

    `events` is an iterable with each element being the name of an inotify
    event as string without the leading ``IN_``. Some interesting event names::

      access: a file was accessed
      attrib: a metadata changed
      close_nowrite: an unwritable file was closed
      close_write: a writable file was closed
      create: a file/directory was created in watched directory
      delete: a file/directory was deleted in watched directory
      delete_self: the watched file was deleted
      modify: a file was modified
      move_self: a watched item was moved
      moved_from: a file/directory in a watched directory was moved from another specified watched directory
      moved_to: a file/directory was moved to another specified watched directory (see move_from)
      onlydir: only watch the path if it is a directory
      open: a file was opened
      unmount: when backing fs was unmounted. Notified to each watch of this fs

    For more information see inotify(7) or the pyinotify documentation at
    https://github.com/seb-m/pyinotify/wiki/Events-types.
    """
    class EventHandler(pyinotify.ProcessEvent):
        def process_default(self, event):
            callback(event)

    wm = _make_watch_manager(paths, events)
    notifier = pyinotify.Notifier(wm, default_proc_fun=EventHandler())
    notifier.loop()


def loop_async(paths, callback, events=(), loop=None):
    """
    Same as `loop` but using asyncio

    `callback` is called without arguments upon any events.
    """
    class EventHandler(pyinotify.ProcessEvent):
        def process_default(self, event):
            callback(event)

    loop = loop if loop is not None else asyncio.get_event_loop()
    wm = _make_watch_manager(paths, events)
    return pyinotify.AsyncioNotifier(wm, loop, default_proc_fun=EventHandler())
