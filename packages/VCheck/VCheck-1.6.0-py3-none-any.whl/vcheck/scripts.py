#!/usr/bin/env python3

import ipdb
import sys as _sys
import argparse as _argparse
import vcheck
from .versionmod import version, hexsha
import builtins as _builtins
# from .checkmod import CheckMod as _CheckMod


def _vcheck():
    # ================================
    # Access command line arguments
    # ================================
    parser = _argparse.ArgumentParser(description=
            'Returns the hash and version of a git repository.')
    parser.add_argument('-V', action='version', version='%(prog)s v{}'.format(vcheck.__version__))
    parser.add_argument('-v', '--verbose', action='store_true',
            help='Verbose mode.')
    parser.add_argument('module',
            help='Module to check.')

    arg = parser.parse_args()

    mod = _builtins.__import__(arg.module)

    def printerr():
        e = _sys.exc_info()
        print(e[1].args[0])

    try:
        print('Hexsha is: {}'.format(hexsha(mod)))
    except:
        printerr()
        return

    try:
        print(version(mod))
    except:
        printerr()


if __name__ == '__main__':
    _vcheck()
