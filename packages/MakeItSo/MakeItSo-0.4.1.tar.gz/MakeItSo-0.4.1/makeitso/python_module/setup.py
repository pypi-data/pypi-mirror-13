import os
from setuptools import setup

try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = file(os.path.join(here, 'README.txt')).read()
except IOError:
    description = None

version = '0.0'

deps = []

setup(name='{{module}}',
      version=version,
      description="{{description}}",
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='{{author}}',
      author_email='{{email}}',
      url='{{url}}',
      license='',
      py_modules=['{{module}}'],
      packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=deps,
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      {{module}} = {{module}}:main
      """,
      )
