#!/usr/bin/env python

from setuptools import setup

CPSVERSION = '1.4.1'

long_description = """
Command line client to ConPaaS, an integrated runtime environment for elastic
Cloud applications
"""
setup(name='cps-tools',
      version=CPSVERSION,
      description='ConPaaS command line client',
      author='ConPaaS team',
      author_email='info@conpaas.eu',
      url='http://www.conpaas.eu/',
      download_url='http://www.conpaas.eu/download/',
      license='BSD',
      packages=['cps_tools'],
      package_dir={'cps_tools': 'src/cps_tools'},
      scripts=['bin/cps-tools',
               'bin/cps-user',
               'bin/cps-application',
               'bin/cps-service',
               'bin/cps-cloud',
               'bin/cps-php',
               'bin/cps-galera'],
      entry_points={'console_scripts': ['cps-tools = cps_tools.cps_tools:main']},
      package_data={'.': ['cps-tools.conf',
                          'bash_completion.d/*']},
      #data_files=[('/etc', ['cps-tools.conf']),
      #            ('/etc/bash_completion.d', ['bash_completion.d/cps-tools'])],
      install_requires=['cpslib', 'argcomplete'],
      dependency_links=['http://www.conpaas.eu/dl/cpslib-%s.tar.gz' % CPSVERSION])
