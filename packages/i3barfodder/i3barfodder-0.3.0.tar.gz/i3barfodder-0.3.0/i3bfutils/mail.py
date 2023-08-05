# Released under GPL3 terms (see LICENSE)

"""Mail account information"""

# TODO: Add MailAccountIMAP class.

from i3bfutils import (io, inotify)
import os.path


def get_account(identifier):
    """
    Return `MailAccount` instance

    `identifier` must be of the format 'PROTOCOL:ACCOUNT'.

    ACCOUNT is used to create a MailAccount object specified by PROTOCOL which
    is then returned.

    The only supported PROTOCOL at the moment is 'maildir'.
    """
    identifier = str(identifier)
    if ':' not in identifier:
        io.croak('Missing protocol in mail account: {!r}'.format(identifier))

    proto, identifier = identifier.split(':', 1)
    if proto.lower() == 'maildir':
        return MailAccountMaildir(identifier)
    else:
        io.croak('Unknown mail protocol: {!r}' .format(proto))


class MailAccount():
    """
    Base class for mail accounts

    Classes derived from this class must implement the method `on_change` and
    the properties `unseen_count` and `seen_count`.
    """
    pass


class MailAccountMaildir(MailAccount):
    """
    Maildir mail account

    `path` must be a directory with subdirectories 'new' and 'cur'.
    """

    def __init__(self, path):
        self._path = os.path.expanduser(path)
        self._path_new = os.path.normpath(self._path+'/new')
        self._path_cur = os.path.normpath(self._path+'/cur')

    def on_change(self, callback):
        """Call `callback` with `unseen_count` and `seen_count` when they change"""
        last_unseen, last_seen = (0, 0)
        def handle_event(event):
            nonlocal last_unseen, last_seen
            unseen, seen = (self.unseen_count, self.seen_count)
            if (last_unseen, last_seen) != (unseen, seen):
                last_unseen, last_seen = (unseen, seen)
                callback(unseen, seen)

        inotify.loop((self._path_new, self._path_cur),
                     callback=handle_event,
                     events=('moved_from', 'moved_to', 'create', 'delete'))
        io.debug('Mail count in {!r} has changed'.format(self._path))

    @property
    def unseen_count(self):
        """Return the number of unseen mails"""
        return self._count_mail(self._path_new)

    @property
    def seen_count(self):
        """Return the number of seen mails"""
        return self._count_mail(self._path_cur)

    def _count_mail(self, path):
        try:
            return len(os.listdir(path))
        except:
            io.croak('Not a maildir directory: {!r}'.format(path))
