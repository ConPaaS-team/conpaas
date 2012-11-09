#!/usr/bin/env python

import os
from setuptools import setup

# find the packages we want to include
wanted_packages = [ 
    elem[0].replace('/', '.') for elem in os.walk('conpaas') 
        if "__init__.py" in elem[2] 
]

long_description = """
ConPaaS: an integrated runtime environment for elastic Cloud applications 
=========================================================================
"""
setup(name='conpaas',
      version='1.1.0',
      description='ConPaaS: an integrated runtime environment for elastic Cloud applications',
      author='Emanuele Rocca',
      author_email='ema@linux.it',
      url='http://www.conpaas.eu/',
      download_url='http://www.conpaas.eu/download/',
      license='BSD',
      packages=wanted_packages)
