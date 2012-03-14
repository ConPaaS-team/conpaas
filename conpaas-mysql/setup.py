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
      zip_safe=False,
    data_files=[
    ('/etc/contrail/conpaas', ['scripts/etc/contrail/conpaas/conpaas-mysql-agent.cnf']),
    ('/etc/contrail/conpaas', ['scripts/etc/contrail/conpaas/conpaas-mysql-manager.cnf']),
    ('/usr/share/contrail/conpaas/mysql/agent', ['scripts/usr/share/contrail/conpaas/mysql/agent/agent.template']),
    ('/usr/share/contrail/conpaas/mysql/agent', ['scripts/usr/share/contrail/conpaas/mysql/agent/init.sh']),
    ('/usr/share/contrail/conpaas/mysql/manager', ['scripts/usr/share/contrail/conpaas/mysql/manager/init.sh']),
    ('/usr/share/contrail/conpaas/mysql/manager', ['scripts/usr/share/contrail/conpaas/mysql/manager/manager.template']),
    ('/usr/share/contrail/conpaas/mysql', ['scripts/usr/share/contrail/conpaas/mysql/conpaas-mysql-agent-server']),
    ('/usr/share/contrail/conpaas/mysql', ['scripts/usr/share/contrail/conpaas/mysql/conpaas-mysql-manager-client']),
    ('/usr/share/contrail/conpaas/mysql', ['scripts/usr/share/contrail/conpaas/mysql/conpaas-mysql-manager-server'])
    ]
      )
