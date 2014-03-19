# -*- coding: utf-8 -*-
#TODO  code cleanup. (This file was cloned from openstack.py. Some parts are not needed.)

"""
    conpaas.core.clouds.federation
    ==============================

    ConPaaS core: Contrail Federation IaaS code.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from ConfigParser import NoOptionError

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from .base import Cloud

import logging
from conpaas.core.log import create_logger, init

DEFAULT_API_VERSION = '0.1'

class FederationCloud(Cloud):

    def __init__(self, cloud_name, iaas_config):
        Cloud.__init__(self, cloud_name)

        cloud_params = [
            'USER', 'PASSWORD', 'HOST',
            'IMAGE_ID', 'SIZE_ID',
            'KEY_NAME',
            'SECURITY_GROUP_NAME',
        ]

        self.__logger = create_logger(__name__)
        self.__logger.setLevel(logging.DEBUG)

        self._check_cloud_params(iaas_config, cloud_params)

        def _get(param):
            return iaas_config.get(cloud_name, param)

        self.user = _get('USER')
        self.passwd = _get('PASSWORD')
        self.host = _get('HOST')
        self.img_id = _get('IMAGE_ID')
        self.size_id = _get('SIZE_ID')
        self.key_name = _get('KEY_NAME')
        self.sg = _get('SECURITY_GROUP_NAME')

        try:
            self.api_version = _get('FEDERATION_VERSION')
        except NoOptionError:
            self.api_version = DEFAULT_API_VERSION

        self.logger.info('Federation cloud ready. API_VERSION=%s' % 
            self.api_version)

    def get_cloud_type(self):
        return 'federation'

    # connect to federation cloud
    def _connect(self):
        FED_ACCESS_ID = ''
        FED_SECRET_KEY = ''
        fedDriver = get_driver(Provider.FEDERATION)

        # self.driver = fedDriver(self.user, self.passwd, secure=False, host=self.host, port=8773, path='/services/Cloud')
        self.driver = fedDriver(FED_ACCESS_ID, FED_SECRET_KEY)
        self.connected = True

    def config(self, config_params={}, context=None):
        if context is not None:
            self._context = context

    def new_instances(self, count, name='conpaas', inst_type=None):
        self.__logger.debug('new_instances')
        if self.connected is False:
            self._connect()

        if inst_type is None:
            inst_type = self.size_id

        class size:
            id = inst_type

        class img:
            id = self.img_id

        kwargs = {
            'size': size,
            'image': img,
            'name': name,
            'ex_mincount': str(count),
            'ex_maxcount': str(count),
            'ex_securitygroup': self.sg,
            'ex_keyname': self.key_name,
            'ex_userdata': self.get_context()
        }

        # TODO   transfer the context to the node
        # return [ self._create_service_nodes(self.driver.create_node(**kwargs)) ]
        #myApp = self.driver.create_node("TestApplication-VU", "small")
        myApp = self.driver.create_node(name, "small")    # TODO replace "small" with user given value
        return [ self._create_service_nodes(myApp, has_private_ip=False) ] # TODO set the correct parameters
        #return [ self._create_service_nodes(self.driver.create_node("TestApplication-VU", "small")) ] # TODO set the correct parameters

def main():
    from pprint import pprint

    from libcloud.compute.types import Provider
    from libcloud.compute.providers import get_driver

    cls = get_driver(Provider.FEDERATION)


if __name__ == '__main__':
    main()

