#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
unit tests for {{package}}
"""

import os
import sys
import tempfile
import unittest

# globals
here = os.path.dirname(os.path.abspath(__file__))

class {{package}}UnitTest(unittest.TestCase):

    def test_{{package}}(self):
        tf = tempfile.mktemp()
        try:
            # pass
            pass
        finally:
            if os.path.exists(tf):
                os.remove(tf)

if __name__ == '__main__':
    unittest.main()
