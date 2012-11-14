#!/usr/bin/env python

import os
from setuptools import setup, find_packages
from setuptools.command import sdist
del sdist.finders[:]

long_description = """
ConPaaS: an integrated runtime environment for elastic Cloud applications 
=========================================================================
"""
setup(name='conpaaslib',
      version='1.1.0',
      description='ConPaaS: an integrated runtime environment for elastic Cloud applications',
      author='Emanuele Rocca',
      author_email='ema@linux.it',
      url='http://www.conpaas.eu/',
      download_url='http://www.conpaas.eu/download/',
      license='BSD',
      packages=find_packages(exclude=["*taskfarm"]),
      install_requires=[ 'simplejson', 'pycurl', 'pyopenssl' ],
      zipfile=None)
