#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
{{description}}
"""

# imports
import argparse
import os
import subprocess
import sys
import time

# python requirements
# (key, value) = (module, PyPI name)
requirements = ()
for module, package in requirements:
    try:
        globals()[module] = __import__(module)
    except ImportError:
        # install requirement and try again
        subprocess.check_call(['pip', 'install', package])
        args = [sys.executable] + sys.argv
        os.execl(sys.executable, *args)

# module globals
__all__ = ['main', 'Parser']
here = os.path.dirname(os.path.realpath(__file__))
string = (str, unicode)

def ensure_dir(directory):
    """ensure a directory exists"""
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            raise OSError("Not a directory: '{}'".format(directory))
        return directory
    os.makedirs(directory)
    return directory


class Parser(argparse.ArgumentParser):
    """CLI option parser"""
    def __init__(self, **kwargs):
        kwargs.setdefault('formatter_class', argparse.RawTextHelpFormatter)
        kwargs.setdefault('description', __doc__)
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_argument('--monitor', dest='monitor',
                          type=float, metavar='SLEEP',
                          help="run in monitor mode")
        self.options = None

    def parse_args(self, *args, **kw):
        options = argparse.ArgumentParser.parse_args(self, *args, **kw)
        self.validate(options)
        self.options = options
        return options

    def validate(self, options):
        """validate options"""

def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    parser = Parser()
    options = parser.parse_args(args)

    try:
        while True:
            if options.monitor:
                time.sleep(options.monitor)
            else:
                break
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()

