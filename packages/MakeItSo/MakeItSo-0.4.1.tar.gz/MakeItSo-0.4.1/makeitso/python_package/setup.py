"""
setup packaging script for {{project}}
"""

import os

version = "0.0"
dependencies = {{dependencies}}

# allow use of setuptools/distribute or distutils
kw = {}
try:
    from setuptools import setup
    kw['entry_points'] = """
{{console_scripts}}
"""
    kw['install_requires'] = dependencies
except ImportError:
    from distutils.core import setup
    kw['requires'] = dependencies

try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = file(os.path.join(here, 'README.txt')).read()
except IOError:
    description = ''


setup(name='{{project}}',
      version=version,
      description="{{description}}",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='{{author}}',
      author_email='{{email}}',
      url='{{url}}',
      license='',
      packages=['{{package}}'],
      include_package_data=True,
      zip_safe=False,
      **kw
      )
