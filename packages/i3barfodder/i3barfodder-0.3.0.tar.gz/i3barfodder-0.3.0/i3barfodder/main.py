# Released under GPL3 terms (see LICENSE file)

from . import (config, worker, constants, error)
import argparse
import os
import logging
import signal
import time
import sys

def handle_error(msg):
    """
    Show error message in logfile and i3bar, then block forever to prevent
    i3bar from showing its generic error message.
    """
    msg = str(msg)
    logging.error(msg)
    msg_i3bar = worker.i3barproto.I3Block(full_text=msg,
                                          color=constants.ERROR_COLOR)
    print('[{}],'.format(msg_i3bar.json))
    try:
        time.sleep(315360000)
    except KeyboardInterrupt:
        exit(0)


class DispatchingFormatter():
    """Use different logging formats per level"""
    def __init__(self, formats, default_format=None):
        self._formatters = {}
        for lvl,frmt in formats.items():
            self._formatters[lvl] = logging.Formatter(frmt, '%H:%M:%S')
        self._default = logging.Formatter(
            fmt=default_format, datefmt='%H:%M:%S'
        )

    def format(self, record):
        if record.levelno in self._formatters:
            formatter = self._formatters[record.levelno]
        elif record.levelname in self._formatters:
            formatter = self._formatters[record.levelname]
        else:
            formatter = self._default
        return formatter.format(record)


def _run():
    # Setup logging
    root_logger = logging.getLogger()
    root_logger.name = 'I3BF'
    log_formatter = DispatchingFormatter(
        { 'DEBUG': '%(asctime)s.%(msecs)03d: [%(name)s] %(levelname)s %(message)s',
          'ERROR': '%(asctime)s.%(msecs)03d: [%(name)s] %(levelname)s %(message)s' },
        default_format='%(asctime)s.%(msecs)03d: [%(name)s] %(message)s'
    )

    # Log to stderr initially
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_formatter)
    root_logger.addHandler(log_handler)

    # Setup command line interface
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('--version', '-V', action='version',
                            version='%(prog)s {}'.format(constants.VERSION))
    cli_parser.add_argument('--debug', '-d', action='count', default=0,
                            help='Increase verbosity level of log messages')
    cli_parser.add_argument('--logfile', '-l',
                            help='Log messages to file instead of stderr')
    cli_parser.add_argument('--config', '-c', default=constants.DEFAULT_CFGFILE,
                            help='Path to configuration file')
    cli_parser.add_argument('--path', '-p', nargs='*',
                            help='Where to look for executables')
    cli = cli_parser.parse_args()

    # Set log level
    if cli.debug >= 2:
        root_logger.setLevel(logging.DEBUG)
    elif cli.debug >= 1:
        root_logger.setLevel(logging.INFO)
    else:
        root_logger.setLevel(logging.WARNING)

    # Redirect logging if set in CLI
    if cli.logfile:
        try:
            config.log_to_file(cli.logfile)
        except error.Config as e:
            handle_error('Can\'t log to {!r}: {!s}'.format(cli.logfile, e))

    # Load config
    try:
        cfgfile = config.Config(cli.config)
    except error.Config as e:
        handle_error('Can\'t read config file {!r}: {!s}'.format(cli.config, e))
    else:
        # Redirect logging if set in config file
        if not cli.logfile and 'logfile' in cfgfile:
            try:
                config.log_to_file(cfgfile['logfile'])
            except error.Config as e:
                handle_error('Can\'t log to {!r}: {!s}'.format(cfgfile['logfile'], e))

        logging.info('i3barfodder version %s', constants.VERSION)

        # Initialize workers
        try:
            workers = worker.WorkerManager(cfgfile)
        except error.Config as e:
            handle_error(str(e))
        else:
            def catch_signal(signum, frame):
                logging.info('Caught %s - Terminating all workers', constants.SIGNAMES[signum])
                workers.terminate()
                exit(0)
            for sig in constants.TERM_SIGNALS:
                signal.signal(sig, catch_signal)

            # Expand PATH variable
            if cli.path:
                for p in cli.path:
                    os.environ['PATH'] += os.pathsep + os.path.expanduser(p)
            if 'PATH' in cfgfile:
                for p in cfgfile['PATH'].split(':'):
                    os.environ['PATH'] += os.pathsep + os.path.expanduser(p)

            # From now on we speak the i3bar protocol
            sys.stdout = worker.i3barproto.I3Stdout()

            # Run workers
            try:
                workers.run()
            except:
                workers.terminate()
                raise

def run():
    try:
        _run()
    except Exception as e:
        logging.exception(e)
        handle_error('Congratulations, you found a bug! '
                     'Send a bug report to collect your prize.')
