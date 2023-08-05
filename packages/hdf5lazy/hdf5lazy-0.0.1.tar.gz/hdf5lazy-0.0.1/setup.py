#!/usr/bin/env python

import os
from setuptools import setup
import sys

setup(name='hdf5lazy',
      version='0.0.1',
      description='Distributed computing',
      maintainer='Matthew Rocklin',
      maintainer_email='mrocklin@gmail.com',
      license='BSD',
      install_requires=[],
      packages=['hdf5lazy'],
      long_description=(open('README.md').read() if os.path.exists('README.md')
                        else ''),
      zip_safe=False)
