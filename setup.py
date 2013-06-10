from distutils.core import setup

with open('README.md') as file:
    long_description = file.read()

setup(name='stockpile',
      long_description=long_description)
