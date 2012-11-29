#!/usr/bin/env python

from setuptools import setup

long_description = """
ConPaaS: an integrated runtime environment for elastic Cloud applications 
=========================================================================
"""
setup(name='cpsclient',
      version='1.1.0',
      description='ConPaaS command line client',
      author='Emanuele Rocca',
      author_email='ema@linux.it',
      url='http://www.conpaas.eu/',
      download_url='http://www.conpaas.eu/download/',
      license='BSD',
      packages=['cps',],
      scripts=['cpsclient.py'],
      install_requires=['cpslib'],
      dependency_links=[ 'http://www.linux.it/~ema/conpaas/cpslib-1.1.0.tar.gz', ],)
