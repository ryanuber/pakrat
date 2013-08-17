# pakrat - A tool for mirroring and versioning YUM repositories.
# Copyright 2013 Ryan Uber <ru@ryanuber.com>. All rights reserved.
#
# MIT LICENSE
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
from setuptools import setup

def required_module(module):
    """ Test for the presence of a given module.

    This function attempts to load a module, and if it fails to load, a message
    is displayed and installation is aborted. This is required because YUM and
    createrepo are not compatible with setuptools, and pakrat cannot function
    without either one of them.
    """
    try:
        __import__(module)
        return True
    except:
        print '\n'.join([
            'The "%s" module is required, but was not found.' % module,
            'Please install the module and try again.'
        ])
        sys.exit(1)

required_module('yum')
required_module('createrepo')

setup(name='pakrat',
    version='0.3.1',
    description='A Python library for mirroring and versioning YUM repositories',
    author='Ryan Uber',
    author_email='ru@ryanuber.com',
    url='https://github.com/ryanuber/pakrat',
    packages=['pakrat'],
    scripts=['bin/pakrat'],
    package_data={'pakrat': ['LICENSE', 'README.md']}
)
