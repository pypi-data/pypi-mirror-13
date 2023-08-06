#!/usr/bin/env python

from setuptools import setup

setup(name='fd',
      version='0.6',
      description='File system database (fd)',
      author='John Emmons',
      author_email='emmons.john@gmail.com',

      install_requires=['filelock', 'pickledb', 'simplejson'],
      py_modules=['fd'],
      scripts=['fd']
     )
