import os
import signal

PROJECTNAME = 'i3barfodder'
VERSION = '0.3.0'

DEFAULT_CFGFILE = os.path.join(os.getenv('XDG_CONFIG_HOME', '') or
                               os.path.join(os.getenv('HOME'), '.config'),
                               PROJECTNAME, 'config')

TERM_SIGNALS = (signal.SIGHUP, signal.SIGINT, signal.SIGPIPE, signal.SIGTERM)
SIGTERM_TIMEOUT = 1
SIGNAMES = dict((getattr(signal, signame), signame.upper())
                for signame in dir(signal)
                if signame.startswith('SIG') and '_' not in signame)

ERROR_COLOR = '#FF4F00'
