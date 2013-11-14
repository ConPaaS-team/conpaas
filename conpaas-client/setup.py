#!/usr/bin/env python

from setuptools import setup

CPSVERSION = '1.3.1'

long_description = """
ConPaaS: an integrated runtime environment for elastic Cloud applications 
=========================================================================
"""
setup(name='cpsclient',
      version=CPSVERSION,
      description='ConPaaS command line client',
      author='ConPaaS team',
      author_email='info@conpaas.eu',
      url='http://www.conpaas.eu/',
      download_url='http://www.conpaas.eu/download/',
      license='BSD',
      packages=['cps',],
      scripts=['cpsclient.py'],
      install_requires=['cpslib'],
      dependency_links=[ 'http://www.conpaas.eu/dl/cpslib-%s.tar.gz' % CPSVERSION, ],)
