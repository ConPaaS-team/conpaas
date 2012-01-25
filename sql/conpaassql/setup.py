#from distutils.core import setup
from setuptools import setup, find_packages

setup(name = 'conpaassql-server',
      version = '0.1',
      description = 'Contrail ConPaaS SQL Server.',
      author = 'Contrail',
      author_email = 'ales.cernivec@xlab.si',
      url = 'http://contrail.eu/',
      #packages = ['conpaas', 'conpaas.mysql','conpaas.mysql.server','conpaas.mysql.server.agent', 'conpaas.mysql.server.manager', 'conpaas.mysql.client','contrib','contrib.libcloud','contrib.libcloud.drivers','contrib.libcloud.storage','contrib.libcloud.storage.drivers','contrib.libcloud.compute','contrib.libcloud.compute.drivers','contrib.libcloud.common'],
      package_dir={'': 'src','contrib':'libcloud'},
      #packages=find_packages('src', 'libcloud'),
      packages=find_packages('src', 'contrib'),
      include_package_data=True,
      classifiers=['Operating System :: POSIX :: Linux',
                   'Programming Language :: Python'],
      zip_safe=False
      )
