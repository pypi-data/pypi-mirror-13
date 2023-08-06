import sys
from setuptools import setup, Extension

version = '0.0.6'
name = 'python_da'
short_description = "`python_da` is Python Double Array Library."
long_description = """\
`python_da` is Python Double Array Library.

Requirements
------------
* Python 2.7 or later (not support 3.x)

Features
--------
* nothing

Setup
-----
::
  $ easy_install python_da

History
-------
0.0.6 (2016-02-04)
------------------
* added support pypy

0.0.1 (2015-04-24)
------------------
* first release
"""

classifiers = [
  "Development Status :: 3 - Alpha",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: C++",
  "Topic :: Software Development :: Libraries"
]

module = Extension('python_da', [
  'ext/python_da.cpp'
], include_dirs=["libda/include"])

if 'PyPy' in sys.version:
    module.libraries.append("stdc++")

setup(name=name,
      version=version,
      description=short_description,
      long_description=long_description,
      classifiers=classifiers,
      keywords=['Data Structure'],
      author="Masahiko Higashiyama",
      author_email="masahiko.higashiyama@gmail.com",
      url='https://github.com/shnya/python_da',
      license='MIT',
      ext_modules=[module],
     )
