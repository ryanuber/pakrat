from setuptools import setup

setup(name='pakrat',
    version='0.0.6',
    description='A Python library for mirroring and versioning YUM repositories',
    author='Ryan Uber',
    author_email='ru@ryanuber.com',
    url='https://github.com/ryanuber/pakrat',
    packages=['pakrat'],
    scripts=['bin/pakrat'],
    package_data={'pakrat': ['LICENSE', 'README.md']}
)
