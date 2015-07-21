#!/usr/bin/env python

from setuptools import setup, find_packages

CPSVERSION = '204'

long_description = """
ConPaaS: an integrated runtime environment for elastic Cloud applications 
=========================================================================
"""
setup(name='cpslib',
      version=CPSVERSION,
      description='ConPaaS: an integrated runtime environment for elastic Cloud applications',
      author='ConPaaS team',
      author_email='info@conpaas.eu',
      url='http://www.conpaas.eu/',
      download_url='http://www.conpaas.eu/download/',
      license='BSD',
      packages=find_packages(), # exclude=["*taskfarm"]),
      install_requires=[ 'simplejson', 'pycurl', 'pyopenssl' ])
