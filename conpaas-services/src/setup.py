#!/usr/bin/env python

from setuptools import setup, find_packages
from setuptools.command import sdist
del sdist.finders[:]

CPSVERSION = '1.1.0-rc3'

long_description = """
ConPaaS: an integrated runtime environment for elastic Cloud applications 
=========================================================================
"""
setup(name='cpslib',
      version=CPSVERSION,
      description='ConPaaS: an integrated runtime environment for elastic Cloud applications',
      author='Emanuele Rocca',
      author_email='ema@linux.it',
      url='http://www.conpaas.eu/',
      download_url='http://www.conpaas.eu/download/',
      license='BSD',
      packages=find_packages(exclude=["*taskfarm"]),
      install_requires=[ 'simplejson', 'pycurl', 'pyopenssl' ])
