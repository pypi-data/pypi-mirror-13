# Released under GPL3 terms (see LICENSE file)

from . import (i3barproto, validation, constants, config, error)
import subprocess
import shlex
import json
import logging
import select
import fcntl
import os
import sys
import logging
import time


class Readpool():
    """Read from multiple file descriptors at once"""

    def __init__(self):
        self._fds = {}  # Map fd -> callback
        self._log = logging.getLogger('IO')

    def add(self, fd, callback):
        """
        Add `fd` to file descriptors to read from

        Lines that appear on `fd` are forwarded as a list to `callback`.
        """
        flags = fcntl.fcntl(fd, fcntl.F_GETFL, 0)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        self._fds[fd] = callback
        # self._log.debug('Registered FD#%s for %s', fd.name, repr(callback))

    def remove(self, fd):
        """Stop reading from `fd`"""
        if fd in self._fds:
            # self._log.debug('Unregistering FD#%s of %s', fd.name, repr(self._fds[fd]))
            del(self._fds[fd])

    def read(self, fd='all', timeout=-1, delay=0):
        """
        Wait for input to appear and call callbacks accordingly

        If `fd` is 'all' or not specified, process all registered file
        descriptors.

        If `timeout` is >= 0, stop waiting for input after that many
        seconds. Otherwise, block indefinitely until there is something to
        read.

        IF `delay` is > 0, if there is something to read, wait `delay` seconds
        and then check all file descriptors again.
        """
        if fd == 'all':
            fds = list(self._fds)
        else:
            fds = [fd]

        if not fds:
            if timeout > 0:
                time.sleep(timeout)
            return

        # self._log.debug('Waiting to read from: %s', ', '.join('FD#'+str(fd.name) for fd in fds))
        if timeout >= 0:
            rlist, _, _ = select.select(fds, [], [], timeout)
        else:
            rlist, _, _ = select.select(fds, [], [])

        if delay > 0:
            # Once there's output available, wait a few msecs before taking
            # action to bundle multiple outputs into one update.
            time.sleep(delay)
            self.read(delay=0, timeout=0)
        else:
            for fd in rlist:
                if fd in self._fds:
                    callback = self._fds[fd]
                    lines = [line.rstrip('\n') for line in fd.readlines()]
                    if len(lines) < 1:
                        # fd is readable but returns not even an empty line ("\n")
                        # Process somehow terminated
                        fd.close()
                        self.remove(fd=fd)
                        # self._log.debug('Reporting dead FD#%s to %s', fd.name, repr(callback))
                        callback([])  # Report dead fd
                    else:
                        # self._log.debug('Sending %d line(s) from FD#%s to %s',
                        #                 len(lines), fd.name, repr(callback))
                        callback(lines)

NAME_FIELD_SEPARATOR = '\u311F'  # null

# TODO: Add 'run_in' and 'run_at' fields to allow running a newly set command
# in the future.
class Worker():
    DEFAULTS = {
        'command': '',
        'shell': False,
        'trigger_updates': True,
        'clicks_enabled': False,
    }

    VALIDATORS_CFG = {
        'command': lambda v: str(v),
        'shell': validation.validate_bool,
        'trigger_updates': validation.validate_bool,
        'clicks_enabled': validation.validate_bool,
    }

    LAST_BLOCK_RESET_KEYS = ('separator', 'separator_block_width')

    def __init__(self, id, readpool, **initial_vars):
        self._readpool = readpool
        self._id = str(id)
        self._proc = None
        self._log = logging.getLogger(self.id)

        self._stdout_cache = json.dumps({'name': self.id, 'full_text': ''})
        self._stdout_pending = False

        self._stdout_timestamps = []
        self._stderr_timestamps = []

        self._cfg = validation.VDict(validators=self.VALIDATORS_CFG,
                                     valid_keys=tuple(self.DEFAULTS),
                                     **self.DEFAULTS)
        self._env = {}

        self._default_block = i3barproto.I3Block()
        self._blocks = {}
        self._blockids = []  # List of _blocks keys to maintain order

        self._rerun_command = False
        self._initialized = False
        self._update(**initial_vars)
        self._initialized = True

    def run(self):
        self._rerun_command = False
        if self.is_static:
            self._proc = None
        else:
            if self._proc is not None:
                # self._log.debug('Previous process %d is not buried yet', self._proc.pid)
                self.terminate()

            if self._cfg['shell']:
                cmd_str = cmd = self._cfg['command']
            else:
                cmd_str = self._cfg['command']
                cmd = shlex.split(os.path.expanduser(self._cfg['command']))
            self._log.info('Executing%s: %s',
                           ' shell command' if self._cfg['shell'] else '', cmd_str)

            env = os.environ.copy()
            env.update(self._env)
            try:
                self._proc = subprocess.Popen(
                    cmd, env=env,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    bufsize=1,  # Line buffering
                    universal_newlines=True, shell=self._cfg['shell']
                )
            except OSError as e:
                self._croak(long='Can\'t execute {}: {}'.format(cmd_str, e.strerror),
                            short='Failed to run {}'.format(cmd_str.split()[0]))
            else:
                # self._log.debug('New process runs with PID=%d, STDOUT=FD#%s, STDERR=FD#%s',
                #                 self._proc.pid, self._proc.stdout.name, self._proc.stderr.name)
                self._readpool.add(self._proc.stdout, self._handle_stdout)
                self._readpool.add(self._proc.stderr, self._handle_stderr)

    def _handle_click(self, click):
        if self.clicks_enabled:
            self._proc.stdin.write(json.dumps(click) + '\n')

    def _handle_stdout(self, lines):
        for line in lines:
            self._parse_command_stdout(line)

        # No lines means fd closed - process terminated
        if len(lines) < 1:
            self._check_command_result()
        else:
            self._check_lps_limit(lines, self._stdout_timestamps, lps_limit=15)

    def _handle_stderr(self, lines):
        for line in lines:
            self._log.info(line)
        self._check_lps_limit(lines, self._stderr_timestamps, lps_limit=100)

    def _check_lps_limit(self, lines, timestamps, lps_limit):
        # Detect if there are too many lines per second on stdout or stderr.
        now = time.time()
        for line in lines:
            timestamps.append(now)
        if len(timestamps) >= 10:
            while len(timestamps) > 10:
                timestamps.pop(0)
            timerange = now - timestamps[0]
            if timerange > 0:
                lps = int(len(timestamps) / timerange)
                if lps >= lps_limit+1:
                    self._croak(long='Logorrhea detected! ({} lines per second)'.format(int(lps)),
                                short=('Terminated for exceeding '
                                       '{} lines per second limit: {}').format(lps_limit, lps))

    def _check_errors(self):
        # Check if any blocks have accumulated any errors
        errors = self._default_block.errors + \
                 [error for blockid in self._blockids
                  for error in self._blocks[blockid].errors]
        if errors:
            self._croak(long=errors, short=errors[-1])
            return True
        else:
            return False

    def _parse_command_stdout(self, line):
        try:
            line = json.loads(line)
        except ValueError:
            self._update(full_text=line)
        else:
            if isinstance(line, dict):
                self._update(**line)
            elif isinstance(line, list):
                self._update_blocks_only(*line)
            else:
                self._update(full_text=str(line))

    def _generate_json(self, **block):
        if block:
            for key in ('name', 'instance', 'separator', 'separator_block_width'):
                if key not in block and key in self._default_block:
                    block[key] = self._default_block[key]
            self._stdout_cache = i3barproto.I3Block(**block).json

        elif len(self._blockids) < 1:
            self._stdout_cache = self._default_block.json
        else:
            self._stdout_cache = ','.join(self._blocks[blockid].json
                                          for blockid in self._blockids)
        if self.triggers_updates:
            self._stdout_pending = True

        # self._log.debug('Generated json: %s', self._stdout_cache)

    def _error_on_i3bar(self, msg):
        self._generate_json(full_text='[{}: {}]'.format(self.id, msg),
                            color=constants.ERROR_COLOR)

    def _croak(self, long=None, short=None):
        if long is not None:
            if isinstance(long, (list, tuple, set)):
                for line in long:
                    self._log.error(line)
            else:
                self._log.error(long)
        if short is not None:
            self._error_on_i3bar(short)
        elif long is not None and len(long) < 78:
            self._error_on_i3bar(long)
        else:
            self._error_on_i3bar('Unknown error')
        self.terminate()

    def _update(self, **update):
        # A single block (i.e. a dict) can make changes to all blocks that
        # previously came in a list (and are cached in self._blocks), set new
        # defaults for future blocks, and also change the Worker's config
        # (e.g. 'command' or 'trigger_updates') and environment variables
        # (which will only take effect when 'command' is instantiated again).
        for key,val in update.items():
            if key in self._default_block.VALID_FIELDS:
                self._update_default_block(key, val)
            elif key in self.VALIDATORS_CFG:
                self._update_cfg(key, val)
            else:
                self._update_env(key, val)

        errors_found = self._check_errors()
        if not errors_found:
            if self._rerun_command:
                # Run command AFTER all other values are processed so changes to
                # environment variables, etc take effect.
                self.run()
            else:
                self._generate_json()

    def _update_cfg(self, key, val):
        try:
            self._cfg[key] = val
        except error.InvalidValue as e:
            self._croak('Invalid {} value: {}'.format(repr(key), e))
        else:
            if self._initialized and key == 'command':
                self._rerun_command = True

    def _update_env(self, key, val):
        self._log.info('Setting environment variable %s = %s', key, repr(val))
        self._env[key] = val

    def _update_default_block(self, key, val):
        self._default_block[key] = val
        for blockid in self._blockids:
            self._update_block(blockid, key, val)
            # self._log.debug('Setting %s of block %s = %s', key, blockid, val)

    def _update_block(self, blockid, key=None, value=None, **values):
        block = self._blocks[blockid]
        if key is not None:
            if value is None:
                raise TypeError("Missing 'value' argument")
            else:
                block[key] = value
        block.update(**values)

    def _update_blocks_only(self, *blocks):
        # A list of blocks can only make changes to each block, not the
        # default block.

        # Preserve correct order of block ids
        new_blockids = []
        for block in blocks:
            blockid = self.id
            try:
                if 'name' in block:
                    blockid += NAME_FIELD_SEPARATOR + str(block['name'])
                if 'instance' in block:
                    blockid += NAME_FIELD_SEPARATOR + str(block['instance'])
            except TypeError as e:
                self._croak(long="Invalid block type: {}".format(block),
                            short='Block type error')
                return
            else:
                if blockid in new_blockids:
                    self._croak(long=('Block name not unique: {!r}'.format(blockid),
                                      ('NAME+INSTANCE must be unique for each block if '
                                       'multiple blocks are provided by a single worker.')),
                                short='Non-unique name field')
                    return
                else:
                    block['name'] = blockid       # Make 'name' field globally unique
                    if 'instance' in block:
                        del block['instance']     # 'instance' is part of 'name'
                    new_blockids.append(blockid)

        # self._log.debug('Block order: %s', new_blockids)

        for blockid in tuple(self._blockids):
            # Remove blocks from cache that are not in new list
            if blockid not in new_blockids:
                # self._log.debug('Removing #%s', blockid)
                self._remove_block(blockid)

        # Update/Add blocks
        for index,(blockid,block) in enumerate(zip(new_blockids,blocks)):
            if blockid not in self._blockids:
                # self._log.debug('Inserting new block #%s at index %s', blockid, index)
                self._blockids.insert(index, blockid)
                self._blocks[blockid] = self._default_block.copy()
            # self._log.debug('Updating #%s with %s', blockid, block)
            self._update_block(blockid, **block)

            # Move blocks if order has changed
            if blockid != self._blockids[index]:
                # self._log.debug('Moving #%s from %s to %s',
                #                 blockid, self._blockids.index(blockid), index)
                self._swap_blocks(self._blockids.index(blockid), index)

        errors_found = self._check_errors()
        if not errors_found:
            # Last (rightmost) block inherits 'separator' and
            # 'separator_block_width' from defaults.
            if self._blocks:
                last_blockid = self._blockids[-1]
                last_block = self._blocks[last_blockid]
                # self._log.debug('Resetting {} of #{}'.format(self.LAST_BLOCK_RESET_KEYS, last_blockid))
                for reset_key in self.LAST_BLOCK_RESET_KEYS:
                    if reset_key in last_block:
                        if reset_key in self._default_block:
                            last_block[reset_key] = self._default_block[reset_key]
                        else:
                            del(last_block[reset_key])  # Use i3bar default

            self._generate_json()

    def _remove_block(self, blockid):
        del(self._blocks[blockid])
        self._blockids.remove(blockid)

    def _swap_blocks(self, i, j):
        blockid = self._blockids[i]
        self._blockids[i] = self._blockids[j]
        self._blockids[j] = blockid

    @property
    def json(self):
        self._stdout_pending = False
        return self._stdout_cache

    @property
    def stdout_pending(self):
        return self._stdout_pending

    @property
    def triggers_updates(self):
        return self._cfg['trigger_updates']

    @property
    def clicks_enabled(self):
        return self._cfg['clicks_enabled']

    @property
    def id(self):
        return self._id

    @property
    def is_static(self):
        return not bool(self._cfg['command'])

    def terminate(self):
        self._rerun_command = False
        if self._proc is not None and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=constants.SIGTERM_TIMEOUT)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._log.error('No reaction - killed after %d seconds', constants.SIGTERM_TIMEOUT)
        self._check_command_result()

    def _check_command_result(self):
        """If process was running, report how it ended"""
        if self._proc is None:
            return  # Any previous process was already checked
        else:
            msg = 'PID %s: ' % self._proc.pid
            self._proc.poll()
            if self._proc.returncode is None:
                self._log.debug(msg + 'Still running')
            else:
                if self._proc.returncode == 0:
                    self._log.info(msg + 'Terminated gracefully')
                elif self._proc.returncode < 0:
                    self._log.info(msg + 'Terminated by %s', constants.SIGNAMES[-self._proc.returncode])
                else:
                    self._log.error(msg + 'Died with exit code %d', self._proc.returncode)
                    self._error_on_i3bar('{} died'.format(self.id))
                self._readpool.remove(self._proc.stdout)
                self._proc = None

    def __repr__(self):
        return '<{} {}>'.format(type(self).__name__, self.id)


class WorkerManager():
    def __init__(self, cfg):
        self._readpool = Readpool()
        self._cfg = cfg
        self._workers = {}  # worker_id -> Worker instance;
                            # worker_id = config section name

        for worker_id in self._cfg.order:
            worker = Worker(worker_id, self._readpool, **self._cfg.sections[worker_id])
            self._workers[worker_id] = worker

        if not self._workers:
            raise error.Config('No workers specified.')

        elif not any(worker.triggers_updates for worker in self._workers.values()):
            raise error.Config(
                'All workers have "trigger_updates" disabled. '
                'Your i3bar will never display anything with this configuration.')

    def run(self):
        """Handle output from all workers simultaneously"""

        if self._cfg['show_updates']:
            self._updates = []  # List of timestamps of each update

        # i3bar sends clicks to our stdin
        self._readpool.add(sys.stdin, self._handle_stdin)

        for worker in self._workers.values():
            worker.run()

        # Update workers that are either static (no command) or don't trigger
        # updates.
        self._update_i3bar()
        while True:
            self._readpool.read(delay=self._cfg['delay'], timeout=1)
            if any(w.stdout_pending for w in self._workers.values()):
                self._update_i3bar()

    def _update_i3bar(self):
        output = '['
        for worker_id in self._cfg.order:
            output += self._workers[worker_id].json + ','

        if hasattr(self, '_updates'):
            duration = 10  # seconds
            now = time.time()
            while self._updates and now - self._updates[0] > duration:
                self._updates.pop(0)

            if self._updates:
                real_duration = now - self._updates[0]
                ups = len(self._updates) / real_duration
                output += ('{"full_text": "%4.1f u/s"}' % ups) + ','
            else:
                output += '{"full_text": " 0.0 u/s"},'
            self._updates.append(time.time())

        output = output[:-1] + '],'
        print(output)

    def _handle_stdin(self, lines):
        for line in lines:
            line = line.strip().strip(',')
            if line == '[':
                continue
            event = json.loads(line)
            if 'name' in event:
                worker_id, name, instance = event['name'].split(NAME_FIELD_SEPARATOR, 2)
                event['name'] = name
                event['instance'] = instance
                self._workers[worker_id]._handle_click(event)
            else:
                raise RuntimeError('Cannot assign event to worker: {}'.format(line))

    def terminate(self):
        for worker in self._workers.values():
            worker.terminate()
