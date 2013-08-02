import sys
from setuptools import setup

def required_module(module):
    try:
        __import__(module)
        return True
    except:
        print '\n'.join([
            'The "%s" module is required, but is not currently installed.\n' % module,
            'Normally, this could be installed automatically, but since the',
            'upstream source does not contain any setup.py file, automatic',
            'installation is not possible.\n',
            'Please install the module by your own means and try again.'
        ])
        sys.exit(1)

required_module('yum')
required_module('createrepo')

setup(name='pakrat',
    version='0.1.7',
    description='A Python library for mirroring and versioning YUM repositories',
    author='Ryan Uber',
    author_email='ru@ryanuber.com',
    url='https://github.com/ryanuber/pakrat',
    packages=['pakrat'],
    scripts=['bin/pakrat'],
    package_data={'pakrat': ['LICENSE', 'README.md']}
)
