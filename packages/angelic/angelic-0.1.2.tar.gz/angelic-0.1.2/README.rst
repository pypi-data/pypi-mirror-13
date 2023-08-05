angelic
=======

An API for daemonization

Installation
------------

From the project root directory::

    $ python setup.py install

Or just install with pip::

    $ pip install angelic

Usage
-----

Add it to the top of your programs::

    from angelic import Daemon
    daemon = Daemon('app_name')

Then wrap your looping function::
    
    @daemon.daemonize
    def loop(...):
        while True:
            ...

Or specify an interval and have it loop automatically and wait specified seconds::

    @daemon.daemonize(interval=10)
    def loop(...):
        ...

Then add to the bottom of your program::

    daemon.run(...)

The arguments to the daemonized function will be passed from the call to run.

Check Argument Parsing below for more options for starting and stopping your daemon.

See an example implementation here: http://pastebin.com/uZjxU99S

Configuration
-------------

Specify a pid_path with that keyword. Otherwise, it will look for pid_path in all
of the possible config paths, and last, /var/run/$DAEMON_NAME.pid will be chosen::

    daemon = Daemon('myapp', pid_path='~/myapp.pid')

The configuration files will be loaded automatically based on the name of the app, unless
config_path is passed to Daemon. See the pypi package confutil_ for more information
about the configuration logic and usage.

.. _confutil: https://pypi.python.org/pypi/confutil

The order that configuration files will be parsed, from most authoritative to least is
(for a daemon named 'spam'):

    - ./.spam.conf
    - ./.spam.cfg
    - ~/.spam.conf
    - ~/.spam.cfg
    - ~/.config/.spam.conf
    - ~/.config/.spam.cfg
    - ~/.config/spam/config.conf
    - ~/.config/spam/config.cfg
    - ~/.config/spam/config
    - /etc/.spam.conf
    - /etc/.spam.cfg
    - /etc/spam/config.conf
    - /etc/spam/config.cfg
    - /etc/spam/config

To specify an explicit configuration file, pass in the path. The interface will be like a dict,
specifically a ConfigObj object::

    daemon = Daemon('myapp', config_path='~/.myapp.config')
    password = daemon.config['password']

Redirecting STDOUT or STDERR
----------------------------

By default, the daemon will still print its stderr to stderr, and squelch stdout.
To change this behavior, either set the keywords to themself, or None for muting::

    # prints stderr to stderr
    daemon = Daemon('myapp')
    # Keeps stdout, but mutes stderr
    daemon = Daemon('myapp', stdout='stdout', stderr=None)
    # Mutes both stdout and stderr
    daemon = Daemon('myapp', stderr=None)
    # Writes stderr to a file at path /var/log/myapp_raw_stderr
    daemon = Daemon('myapp', stderr='/var/log/myapp_raw_stderr')

It is recommended to keep stderr (default) so that you can debug exceptions in your program.
   
Logging
-------

A simple logger can be instanciated with the Daemon by passing in an argument to its
log paths. For example::

    daemon = Daemon(debug_log='/var/log/myapp_debug.log', error_log='/var/log/myapp_error.log')
    daemon.log.error('Encountered an error!')

Other possible logger arguments are info_log, warning_log, and critical_log.
If not provided in the keyword arguments, the configuration will be checked for debug_log, etc.


Argument Parsing
----------------

A simple start, stop, restart, status interface can be given with the following code::

    daemon.parse_args()

To add arguments to the start command which will pass to the loop, do the following, create the subparsers first::
    
    @daemonize
    def loop(debug=False):
        ...

    def main():
        import argparse
        parser = argparse.ArgumentParser()
        subparsers = daemon.setup_args(parser)
        subparsers['start'].add_argument('--debug', '-d', action='store_true')
        daemon.parse_args(parser)
    
Release Notes
-------------

:0.1.2:
    Just updated README with the simpler argparse functionality.
:0.1.1:
    Removed requirement to create argparser ArgumentParser.
    Now, start/stop/restart/status interface can be created with just `daemon.parse_args()`
:0.1.0:
    Daemonization works according to examples in this README
:0.0.1:
    Project created
