#!/usr/bin/env python
"""
PyPLE (say "pipple") -- the Python Persistent Logic Engine

setup.py: Distutils script

Copyright (C) 2006-2007 Ansel Halliburton.
All rights reserved.

BSD License:

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the PyPLE Project nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

#from distutils.core import setup
from setuptools import setup, find_packages

setup(
  name='pyple',
  version='0.3.1',
  description='PyPLE (pronounced "pipple") is the Python Persistent Logic Engine -- a framework for composing, evaluating, and storing logical expressions.',
  author='Ansel Halliburton',
  author_email='github@anseljh.com',
  keywords=['logic','engine','expression','database'],
  url='https://github.com/anseljh/pyple',
  license='BSD License',
  classifiers=['Development Status :: 2 - Pre-Alpha', 'Intended Audience :: Developers', 'License :: OSI Approved :: BSD License', 'Operating System :: OS Independent', 'Programming Language :: Python', 'Topic :: Software Development :: Libraries :: Python Modules'],
  py_modules=['pyple'],
  package_data = {'':['*.*']},
  packages = find_packages(),
)
