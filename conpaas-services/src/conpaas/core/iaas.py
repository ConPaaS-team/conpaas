# -*- coding: utf-8 -*-

"""
    conpaas.core.iaas
    =================

    ConPaaS core: get cloud objects.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

def get_cloud_instance(cloud_name, cloud_type, iaas_config):
    if cloud_type == 'opennebula':
        from .clouds.opennebula import OpenNebulaCloud
        return OpenNebulaCloud(cloud_name, iaas_config)
    elif cloud_type == 'ec2':
        from .clouds.ec2 import EC2Cloud
        return EC2Cloud(cloud_name, iaas_config)
    elif cloud_type == 'openstack':
        from .clouds.openstack import OpenStackCloud
        return OpenStackCloud(cloud_name, iaas_config)
    elif cloud_type == 'dummy':
        from .clouds.dummy import DummyCloud
        return DummyCloud(cloud_name, iaas_config)
    elif cloud_type == 'federation':
        # ConPaaS running in federation mode
        pass


def get_clouds(iaas_config):
    '''Parses the config file containing the clouds'''
    return [get_cloud_instance(cloud_name,
                               iaas_config.get(cloud_name, 'DRIVER').lower(),
                               iaas_config)
            for cloud_name in iaas_config.get('iaas', 'OTHER_CLOUDS').split(',')
            if iaas_config.has_section(cloud_name)]
