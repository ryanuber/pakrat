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
    version='0.3.2',
    description='A tool for mirroring and versioning YUM repositories',
    author='Ryan Uber',
    author_email='ru@ryanuber.com',
    url='https://github.com/ryanuber/pakrat',
    packages=['pakrat'],
    scripts=['bin/pakrat'],
    package_data={'pakrat': ['LICENSE', 'README.md']}
)
