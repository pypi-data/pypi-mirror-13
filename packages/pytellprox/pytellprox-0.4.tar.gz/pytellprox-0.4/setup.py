#!/usr/bin/env python3

from distutils.core import setup

setup(name='pytellprox',
      version='0.4',
      license='GPLv3',
      description='Python bindings for the Tellprox API',
      long_description=open('README.md', 'r').read(),
      author='Christian Bryn',
      author_email='chr.bryn@gmail.com',
      url='https://github.com/epleterte/pytellprox',
      platform='Linux',
      py_modules=['tellprox'],
      #packages=['pytellprox'],
     )
