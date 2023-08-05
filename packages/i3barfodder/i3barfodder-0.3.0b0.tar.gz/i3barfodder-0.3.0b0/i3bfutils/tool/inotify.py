# Released under GPL3 terms (see LICENSE)

"""Convenient pyinotify wrapper"""

from . import io
import asyncio
import os
try:
    import pyinotify
except ImportError:
    io.croak('Please install python3-pyinotify')


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


def wait(*paths, events=()):
    """
    Block until one of `events` happened for one of `paths`

    `events` is an iterable with each element being the name of an inotify
    event (as a string). The most interesting events are:

      ACCESS: a file was accessed
      ATTRIB: a metadata changed
      CLOSE_NOWRITE: an unwritable file was closed
      CLOSE_WRITE: a writable file was closed
      CREATE: a file/directory was created in watched directory
      DELETE: a file/directory was deleted in watched directory
      MODIFY: a file was modified
      MOVE_SELF: a watched item was moved
      MOVED_FROM: a file/directory in a watched directory was moved from another specified watched directory
      MOVED_TO: a file/directory was moved to another specified watched directory (see IN_MOVE_FROM)
      ONLYDIR: only watch the path if it is a directory
      OPEN: a file was opened
      UNMOUNT: when backing fs was unmounted. Notified to each watch of this fs

    For more information see the pyinotify documentation[1] or inotify(7).

    [1]: https://github.com/seb-m/pyinotify/wiki/Events-types
    """
    wm = _make_watch_manager(paths, events)
    notifier = pyinotify.Notifier(wm)
    notifier.process_events()
    if notifier.check_events():
        notifier.read_events()


def wait_async(*paths, events=(), callback=None, loop=None):
    """
    Same as `wait` but using asyncio

    `callback` is called without arguments upon any events.
    """
    loop = loop if loop is not None else asyncio.get_event_loop()
    eventmask = _make_event_mask(events)
    wm = _make_watch_manager(paths, events)

    class EventHandler(pyinotify.ProcessEvent):
        def process_default(self, event):
            callback(event)

    pyinotify.AsyncioNotifier(wm, loop, default_proc_fun=EventHandler())
