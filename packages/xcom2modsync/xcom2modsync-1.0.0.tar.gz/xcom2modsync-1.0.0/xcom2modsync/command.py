"""Implements the command-line interface for XCOM2 Mod Synchronizer.

Usage:
  xcom2modsync [options]
  xcom2modsync --version
  xcom2modsync --help

Options:
  --workshop-path   Path to Steam Workshop's root directory
  --mods-path       Path to XCOM2's mod directory

"""

from __future__ import print_function
import sys
from docopt import docopt
from . import __version__, Synchronizer, DEFAULT_MODS_PATH, DEFAULT_XCOM2_WORKSHOP_PATH

version = 'xcom2modsync ' + __version__


def main():
    """
    The entry point of the application.
    """
    args = docopt(__doc__, argv=sys.argv[1:], version=version, options_first=True)

    workshop_path = args['--workshop-path'] or DEFAULT_XCOM2_WORKSHOP_PATH
    mods_path = args['--mods-path'] or DEFAULT_MODS_PATH

    Synchronizer(workshop_path, mods_path).run()
    return 0

