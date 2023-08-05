#!/usr/bin/env python
''' angelic.daemon
API for daemonization
'''
import sys
import os
import signal
import time

from configobj import ConfigObj
from confutil import Config
from tinylog import Logger


def _fork():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit()
    except OSError as e:
        sys.stderr.write('Failed to fork (errno %d): %s\n' % (
            e.errno, e.strerror))
        sys.exit(1)


def _flush_sys():
    sys.stdin.flush()
    sys.stdout.flush()
    sys.stderr.flush()


def _dup_fds(stdout=None, stderr=None):
    ''' Duplicate /dev/null into stdin, stdout, and stderr '''
    if stdout is None:
        stdout = os.devnull
    if stderr is None:
        stderr = os.devnull
    _stdin = file(os.devnull, 'r')
    if isinstance(stdout, basestring):
        _stdout = file(stdout, 'a+')
    else:
        _stdout = stdout
    if isinstance(stderr, basestring):
        _stderr = file(stderr, 'a+', 0)
    else:
        _stderr = stderr
    # Duplicate into sys std files
    try:
        os.dup2(_stdin.fileno(), sys.stdin.fileno())
        os.dup2(_stdout.fileno(), sys.stdout.fileno())
        os.dup2(_stderr.fileno(), sys.stderr.fileno())
    except OSError as e:
        sys.stderr.write('dup2 failed (errno %d): %s\n' % (
            e.errno, e.strerror))
        sys.exit(1)


def _setup_sigs(sig_handler):
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)


def _new_session():
    os.setsid()
    os.umask(022)


def _daemonize(sig_handler, stdout=None, stderr=None):
    _fork()
    _new_session()
    _fork()
    _flush_sys()
    _dup_fds(stdout=stdout, stderr=stderr)
    _setup_sigs(sig_handler)


class Daemon(object):

    def __init__(self, name, config_path=None, pid_path=None,
                 console=None, debug_log=None, info_log=None, warning_log=None,
                 error_log=None, critical_log=None,
                 stdout=None, stderr='stderr'):
        self.name = name
        if config_path is not None:
            self.config = ConfigObj(config_path)
        else:
            self.config = Config(name)
        self.pid_path = (
            pid_path or self.config.get('pid_path') or
            ('/var/run/%s.pid' % name))
        self.pid_path = os.path.expanduser(self.pid_path)
        logger_kwargs = {
            'console': console or self.config.get('console_log'),
            'debug': debug_log or self.config.get('debug_log'),
            'info': info_log or self.config.get('info_log'),
            'warning': warning_log or self.config.get('warning_log'),
            'error': error_log or self.config.get('error_log'),
            'critical': critical_log or self.config.get('critical_log'),
        }
        self.log = None
        self.log_stdout = False
        self.log_stderr = False
        self.looping_func = None
        self.starting_func = None
        self.stopping_func = None
        self.stdout = stdout
        self.stderr = stderr
        if self.stdout in ('stdout', 'stderr'):
            self.stdout = getattr(sys, self.stdout)
        elif self.stdout in (None, 'devnull', '/dev/null'):
            self.stdout = os.devnull
        else:
            self.stdout = open(self.stdout, 'a+')
        if self.stderr in ('stdout', 'stderr'):
            self.stderr = getattr(sys, self.stderr)
        elif self.stderr in (None, 'devnull', '/dev/null'):
            self.stderr = os.devnull
        else:
            self.stderr = open(self.stderr, 'a+')
        if any(logger_kwargs.values()):
            for k, v in logger_kwargs.items():
                if v:
                    logger_kwargs[k] = os.path.expanduser(v)
            self.log = Logger(**logger_kwargs)
            self.log_stdout = self.log._stdout
            self.log_stderr = self.log._stderr

    def daemonize(self, *args, **kwargs):

        def decorator(func):
            self.looping_func = func

            def wrapped(*fargs, **fkwargs):
                return func(*fargs, **fkwargs)
            return wrapped

        self.interval = None
        if 'interval' in kwargs:
            self.interval = kwargs['interval']

        if len(args) == 1 and not kwargs:
            return decorator(args[0])

        return decorator

    def setup_sig_handler(self):
        def signal_handler(signum, frame):
            try:
                if self.stopping_func is not None:
                    self.stopping_func()
            except:
                if self.log:
                    self.log.error('Could not run @stop function')
            finally:
                self.del_pid()
                sys.exit()
        return signal_handler

    def run(self, *args, **kwargs):
        if not self.looping_func:
            raise RuntimeError('No function is set to daemonize.\n'
                               'Decorate your looping function with '
                               'daemon.daemonize.\n'
                               'See documentation for more information.')
        pid = self.check_status()
        if pid is not None:
            sys.stderr.write('Daemon already running as PID %d\n' % pid)
            sys.exit(1)
        _daemonize(self.setup_sig_handler(), stdout=self.stdout,
                   stderr=self.stderr)
        self.write_pid()
        if self.starting_func is not None:
            self.starting_func(*args, **kwargs)
        if self.interval is not None:
            while True:
                self.looping_func(*args, **kwargs)
                time.sleep(self.interval)
        else:
            self.looping_func(*args, **kwargs)

    def write_pid(self):
        pid = os.getpid()
        try:
            with open(self.pid_path, 'w+') as f:
                f.write('%d\n' % pid)
        except Exception as e:
            sys.stderr.write('Failed to write PID %s to %s (errno %d): %s\n' % (
                str(pid), self.pid_path, e.errno, e.strerror))
            sys.exit(1)

    def get_pid(self):
        pid = None
        if os.path.exists(self.pid_path):
            try:
                with open(self.pid_path) as f:
                    s_pid = f.read().strip()
            except Exception as e:
                sys.stderr.write('Failed to read PID from %s (errno %d): %s\n'
                                 % (self.pid, e.errno, e.strerror))
                sys.exit(1)
            if not s_pid.isdigit():
                sys.stderr.write('PID file is not digit: %s\n' % s_pid)
                sys.exit(1)
            pid = int(s_pid)
        return pid

    def del_pid(self):
        if os.path.exists(self.pid_path):
            os.remove(self.pid_path)

    def die(self, *args, **kwargs):
        self.signal_handler(None, None)

    def start(self, func):
        self.starting_func = func

        def decorated(*args, **kwargs):
            return func(*args, **kwargs)
        return decorated

    def stop(self, func):
        self.stopping_func = func

        def decorated(*args, **kwargs):
            return func(*args, **kwargs)
        return decorated

    def setup_args(self, parser):
        subs = parser.add_subparsers(dest='cmd')
        p_start = subs.add_parser('start')
        subs.add_parser('stop')
        p_restart = subs.add_parser('restart')
        subs.add_parser('status')
        return {'start': p_start, 'restart': p_restart}

    def check_status(self):
        pid = self.get_pid()
        if pid is None:
            return None
        if os.path.exists('/proc/%d' % pid):
            return pid
        else:
            self.del_pid()
            return None

    def print_status(self, pid):
        if pid:
            sys.stderr.write('%s is running with PID %d\n' % (self.name, pid))
            sys.exit(0)
        else:
            sys.stderr.write('%s is stopped.\n' % (self.name))
            sys.exit(1)

    def kill_pid(self):
        pid = self.get_pid()
        if pid is None:
            return False
        if os.path.exists('/proc/%d' % pid):
            os.kill(pid, signal.SIGTERM)
            return True
        return False

    def parse_args(self, parser):
        args = parser.parse_args()
        cmd = args.cmd
        kwargs = dict(args._get_kwargs())
        del kwargs['cmd']
        if cmd == 'start':
            self.run(**kwargs)
            if self.get_pid() is not None:
                sys.exit(0)
            sys.exit(1)
        elif cmd == 'stop':
            if not self.kill_pid():
                sys.exit(1)
            sys.exit(0)
        elif cmd == 'restart':
            self.kill_pid()
            self.run(**kwargs)
            if self.get_pid() is not None:
                sys.exit(0)
            sys.exit(1)
        elif cmd == 'status':
            pid = self.check_status()
            self.print_status(pid)
