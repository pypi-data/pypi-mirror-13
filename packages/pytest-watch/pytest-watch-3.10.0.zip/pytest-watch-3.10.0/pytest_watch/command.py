"""
pytest_watch.command
~~~~~~~~~~~~~~~~~~~~

Implements the command-line interface for pytest-watch.

All positional arguments after `--` are passed directly to py.test executable.


Usage: ptw [options] [<directories>...] [-- <args>...]

Options:
  -h --help         Show this help.
  --version         Show version.
  --ignore=<dirs>   Comma-separated list of directories to ignore
                    (if relative: starting from the root of each watched dir).
  -c --clear        Automatically clear the screen before each run.
  --beforerun=<cmd> Run arbitrary command before tests are run.
  --onpass=<cmd>    Run arbitrary command on pass.
  --onfail=<cmd>    Run arbitrary command on failure.
  --onexit=<cmd>    Run arbitrary command when exiting.
  --runner=<cmd>    Run a custom command instead of py.test.
  --nobeep          Do not beep on failure.
  -p --poll         Use polling instead of events (useful in VMs).
  --ext=<exts>      Comma-separated list of file extensions that trigger a
                    new test run when changed (default: .py).
  --no-spool        Disable event spooling (default: 200ms cooldown).
  -v --verbose      Increase verbosity of the output.
  -q --quiet        Decrease verbosity of the output
                    (takes precedence over verbose).
"""

import sys

import colorama
from docopt import docopt

from . import __version__
from .watcher import watch
from .config import merge_config


usage = '\n\n\n'.join(__doc__.split('\n\n\n')[1:])
version = 'pytest-watch ' + __version__


def main(argv=None):
    """
    The entry point of the application.
    """
    if argv is None:
        argv = sys.argv[1:]

    # Initialize terminal colors
    colorama.init()

    # Parse CLI arguments
    args = docopt(usage, argv=argv, version=version)

    # Split paths and pytest arguments
    pytest_args = []
    directories = args['<directories>']
    if '--' in directories:
        index = directories.index('--')
        directories, pytest_args = directories[:index], directories[index + 1:]

    # Merge config file options
    merge_config(args, directories)

    ignore = (args['--ignore'] or '').split(',')
    extensions = [('.' if not ext.startswith('.') else '') + ext
                  for ext in (args['--ext'] or '.py').split(',')]

    # Run pytest and watch for changes
    return watch(directories=directories,
                 ignore=ignore,
                 auto_clear=args['--clear'],
                 beep_on_failure=not args['--nobeep'],
                 onpass=args['--onpass'],
                 onfail=args['--onfail'],
                 runner=args['--runner'],
                 beforerun=args['--beforerun'],
                 onexit=args['--onexit'],
                 poll=args['--poll'],
                 extensions=extensions,
                 args=pytest_args,
                 spool=not args['--no-spool'],
                 verbose=args['--verbose'],
                 quiet=args['--quiet'])
