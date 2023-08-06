#!/usr/bin/env python

"""
{{project}} template for makeitso
"""

import sys
from cli import MakeItSoCLI
from optparse import OptionParser
from template import MakeItSoTemplate

class {{project}}Template(MakeItSoTemplate):
  """
  {{project}} template
  """
  name = '{{project}}'
  templates = ['template']
  look = True

class TemplateCLI(MakeItSoCLI):
  """
  CLI driver for the {{project}} template
  """

def main(args=sys.argv[:]):
  cli = TemplateCLI()
  cli(*args)
  
if __name__ == '__main__':
  main()  

