# Released under GPL3 terms (see LICENSE)

"""Various input/output functions"""

import os
import sys
import json
import subprocess
import importlib


def push(output=None, **kwargs):
    """
    Print `output` and flush stdout

    If `output` is dict-like or list-like, it is printed as JSON on a single
    line.
    """
    if output is not None:
        if isinstance(output, (set, tuple)):
            output = list(output)
        if isinstance(output, (dict, list)):
            output = json.dumps(output)
        print(output, flush=True)
    else:
        print(json.dumps(kwargs), flush=True)


def debug(*msgs):
    """Print `msgs` to stderr"""
    print(' '.join(str(m) for m in msgs), file=sys.stderr, flush=True)


def croak(errmsg, exitcode=1):
    """Print `errmsg` and exit with `exitcode`"""
    print(errmsg, file=sys.stderr, flush=True)
    exit(exitcode)


def get_var(variable, default=None, unset_msg=None, options=()):
    """
    Return value of environment `variable`

    If `default` is None, an error is printed to STDERR if the variable is not
    set. `unset_msg`, if not None, is a custom error message, otherwise one is
    generated.

    If `default` is not None, it is returned if the variable is not set.

    If the environment variable is set, its value is converted to `default`'s
    type.  If `default` is a `list`, `set` or `tuple`, "," is used as the
    separator and `default` is returned as a `list`.

    Valid boolean values are true/false, yes/no, on/off and 1/0 (case is
    ignored).

    If `options` is a non-empty iterable, `variable`'s value must be a member
    of it.
    """
    value = os.environ.get(variable, default)
    if value is None:
        if unset_msg is None:
            unset_msg = '{} is not set'.format(variable)
        croak(unset_msg)

    if default is not None:
        # Bools are special because python considers every non-empty string as True.
        if type(default) is bool and options == ():
            if str(value).lower() in ('true', 'yes', 'on', '1'):
                return True
            elif str(value).lower() in ('false', 'no', 'off', '0'):
                return False
            else:
                croak('Invalid boolean value: {!r}'.format(value))

        # Lists are comma-separated
        elif isinstance(default, (list, tuple, set)) and isinstance(value, str):
            value = [item.strip() for item in value.split(',') if value.strip()]

        elif type(value) != type(default):
            try:
                value = type(default)(value)
            except Exception:
                croak('Invalid {} value: {!r}'.format(variable, value))

    if options and value not in options:
        croak('{} must be one of: {}'
              .format(variable, ', '.join(repr(o) for o in options)))

    return value


def read_file(path):
    """Return contents from file `path` without trailing newlines"""
    try:
        content = open(path, 'r').readline().strip('\n')
    except OSError as e:
        croak('Unable to read {!r}: {}'.format(path, e.strerror))
    return content


def run(cmd, placeholders={}):
    """Run `cmd` in a shell and pass STDOUT and STDIN to `debug`

    If `placeholders` is given, it will applied to `cmd` thusly::

        cmd.format(**placeholders)
    """
    if placeholders:
        try:
            cmd = cmd.format(**placeholders)
        except KeyError as key:
            io.debug('Missing placeholder for command {!r}: {}'.format(cmd_tmplt, key))

    debug('Executing: {}'.format(cmd))
    proc = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for out in (proc.stdout, proc.stderr):
        for line in out:
            debug(line.rstrip('\n'))
    proc.wait()
    if proc.returncode:
        debug('Command died with return code {}: {}'.format(proc.returncode, cmd))


def handle_click(click, **callbacks):
    """Handle `click` as returned by `delay.wait_for_clicks`

    `callbacks` maps 'buttonN' keys to callables, N being the number of a
    mouse button starting at 1.

    `click` is passed on to the callback.
    """
    if click is None:
        return
    else:
        button = 'button' + str(click.get('button'))
        try:
            callback = callbacks[button]
        except KeyError:
            pass
        else:
            callback(click)


def import_or_croak(module):
    """Return imported non-standard module or `croak` with helpful error message"""
    try:
        return importlib.import_module(module)
    except ImportError:
        msg = ('Could not find {!r} module for Python 3.'.format(module),
               ("Depending on your distro, the package might be named "
                "'python3-{0}' or 'python-{0}'.".format(module)))
        croak('\n'.join(msg))
