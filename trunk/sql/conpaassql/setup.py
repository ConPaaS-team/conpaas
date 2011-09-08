from distutils.core import setup

setup(name = 'conpaassql-server',
      version = '0.1',
      description = 'Contrail ConPaaS SQL Server.',
      author = 'Ales Cernivec',
      author_email = 'ales.cernivec@xlab.si',
      url = 'http://contrail.eu/',
      packages = ['conpaas', 'conpaas.mysql','conpaas.mysql.server','conpaas.mysql.server.agent', 'conpaas.mysql.server.manager', 'conpaas.mysql.client','contrib','contrib.libcloud','contrib.libcloud.drivers','contrib.libcloud.storage','contrib.libcloud.storage.drivers','contrib.libcloud.compute','contrib.libcloud.compute.drivers','contrib.libcloud.common'],
      package_dir = { 'conpaas': 'src/conpaas','contrib' : 'contrib' })

