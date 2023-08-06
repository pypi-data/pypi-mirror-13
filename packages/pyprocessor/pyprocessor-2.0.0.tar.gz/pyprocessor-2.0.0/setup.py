#!/usr/bin/env python3

from distutils.core import setup
import pyprocessor

setup(
  name='pyprocessor',
  version=pyprocessor.__version__,
  description='Python 3 Preprocessor',
  url='https://github.com/alkafir/pyprocessor',
  author='Alfredo Mungo',
  author_email='alfredo.mungo@openmailbox.org',
  license='GPLv3+',
  classifiers = (
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Environment :: Console',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.5',
    'Topic :: Software Development :: Pre-processors',
    'Topic :: Software Development :: Libraries :: Python Modules',
  ),
  keywords='pre-processor',
  py_modules=('pyprocessor',)
)
