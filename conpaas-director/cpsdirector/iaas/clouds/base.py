# -*- coding: utf-8 -*-

"""
    conpaas.core.clouds.base
    ========================

    ConPaaS core: cloud-independent IaaS code.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""
import time
from itertools import chain
from string import Template

from conpaas.core.node import ServiceNode, ServiceVolume
from conpaas.core.log import create_logger

class Cloud:
    ''' Abstract Cloud '''

    def __init__(self, cloud_name):
        #TODO: it shouldn't be cloud_name == config file section name
        self.cloud_name = cloud_name
        self.connected = False
        self.driver = None
        self._context = None
        self._mapping_vars = {}
        self.logger = create_logger(__name__)

    def get_cloud_name(self):
        return self.cloud_name

    def _check_cloud_params(self, iaas_config, cloud_params=[]):
        """Check for missing or empty parameters in iaas_config"""
        error_template = '%s config param %s for %s'

        for field in cloud_params:
            if not iaas_config.has_option(self.cloud_name, field):
                raise Exception('Missing ' + error_template % (
                    self.get_cloud_type(), field, self.cloud_name
                ))

            if iaas_config.get(self.cloud_name, field) == '':
                raise Exception('Empty ' + error_template % (
                    self.get_cloud_type(), field, self.cloud_name
                ))

        return None

    def _connect(self):
        '''
        _connect is the method used to set the driver and connect to the cloud

        '''
        raise NotImplementedError(
            '_connect not implemented for this cloud driver')

    def get_cloud_type(self):
        raise NotImplementedError(
            'get_cloud_type not implemented for this cloud driver')


    def set_context(self, new_context):
        """
        Sets the context for this cloud.
        """
        self._context = new_context


    def add_context_replacement(self, replace={}, strict=False):
        """Add a variable replacement to the variable replacements to apply to
           the context as a template.

            @param replace A dictionary that specifies which words shoud be
                           replaced with what. For example:
                           replace = dict(name='A', age='57')
                           context1 =  '$name , $age'
                           => new_context1 = 'A , 57'
                           context2 ='${name}na, ${age}'
                           => new_context2 = 'Ana, 57'
            
            @param strict  If true, then setting a replacement for an already
                           replaced variable will raise an exception.

        """
        
        if strict: 
            intersect_vars = set(self.mapping_vars.keys()).intersection(set(replace.keys()))
            if len(intersect_vars) != 0:
                raise Exception('Cannot overwrite replacements for variables %s in strict mode. \
                        Existing replacements are %s. Conflicting new replacements are %s' \
                        % (intersect_vars, self._mapping_vars, replace))
        self._mapping_vars = dict(chain(self._mapping_vars.items(), replace.items()))


    def get_context(self):
        """
        Returns the context.
        Apply the replacement variables if any.
        Return an empty string if it has not been set. 
        """
        if self._context is not None:
            return Template(self._context).safe_substitute(self._mapping_vars)
        else:
            return None


    def config(self, config_params, context):
        raise NotImplementedError(
            'config not implemented for this cloud driver')

    def list_vms(self, has_private_ip=True):
        '''
        lists the service nodes in the cloud instances

        @return vms: List[ServiceNode]

        '''
        self.logger.debug('list_vms(has_private_ip=%s)' % has_private_ip)

        if self.connected is False:
            self._connect()

        # FIXME put the volumes here 
        volumes = []
        return [serviceNode for serviceNode in
                self._create_service_nodes(self.driver.list_nodes(), volumes)]

    # def new_instances(self, count, name='conpaas', inst_type=None, volumes={}):
    #     raise NotImplementedError(
    #         'new_instances not implemented for this cloud driver')

    def new_instances(self, nodes_info):
        raise NotImplementedError(
            'new_instances not implemented for this cloud driver')

    def _create_service_nodes(self, instances, instances_info=None, has_private_ip=True):
        '''
        creates a list of ServiceNode

        @param  instances: List of nodes provide by the driver or a single node
        @type   instances: L{libcloud.compute.Node} or C{libcloud.compute.Node}

        @param  has_private_ip: some instances only need the public ip
        @type   has_private_ip: C{bool}

        '''
        volumes = []
        if type(instances) is list:
            ret = []
            for node in instances:
                role = 'manager'
                if instances_info and len(instances_info) > 0:
                    node_info = filter(lambda n: n['id']==node.id, instances_info)[0]
                    if 'volumes' in node_info:
                        volumes = node_info['volumes']
                    role = node_info.get('role', 'node')
                ret += [self.__create_one_service_node(node, volumes, has_private_ip, role)]
            return ret

        
        node_info = filter(lambda n: n['id']==instances.id, instances_info)[0] 
        if 'volumes' in node_info:
            volumes = node_info['volumes']
        role = node_info.get('role', 'node')
        return self.__create_one_service_node(instances, volumes, has_private_ip, role)

    def __create_one_service_node(self, instance, volumes, has_private_ip=True, role='node'):
        '''
        creates a single ServiceNode

        @param  instance: node provided by the driver
        @type   instance: C{libcloud.compute.Node}

        @param  has_private_ip: some instances only need the public ip
        @type   has_private_ip: C{bool}

        '''
        ip, private_ip = self.__get_ips(instance, has_private_ip)
        sn = ServiceNode(instance.id, ip, private_ip, self.cloud_name, role=role)
        svols = [ServiceVolume.from_dict(volume) for volume in volumes]
        if len(svols) > 0:
            sn.volumes = svols
        return sn

    def __get_ips(self, instance, has_private_ip):
        if instance.public_ips:
            ip = instance.public_ips[0]
        else:
            ip = ''
        if has_private_ip:
            if instance.private_ips:
                private_ip = instance.private_ips[0]
            else:
                private_ip = ''
        else:
            private_ip = ip

        if hasattr(ip, 'address'):
            ip = ip.address

        if hasattr(private_ip, 'address'):
            private_ip = private_ip.address

        return ip, private_ip

    def kill_instance(self, node):
        '''Kill a VM instance.

           @param node: A ServiceNode instance, where node.id is the
                        vm_id
        '''
        self.logger.debug('kill_instance(node=%s)' % node)

        if self.connected is False:
            self._connect()

        libcloud_node = node.as_libcloud_node()

        # Delete also the volumes atached to the node (not sure if this is cross-cloud)

        # (teodor) This of course does not work on Amazon EC2.
        #          For the moment, I ignore any exception thrown, which will result in
        #          volumes not being deleted on EC2.
        # TODO:    This needs to be fixed asap.!

        
        # volumes = filter(lambda x: False if len(x.extra['attachments'])==0 else x.extra['attachments'][0]['serverId']==libcloud_node.id, self.driver.list_volumes())
        volumes = self.list_instance_volumes(libcloud_node)
        self.logger.debug('delete these volumes: %s' % volumes)
        
        for volume in volumes:
            max_trials = 20
            self.detach_volume(volume)
            status=volume.extra['state']
            while status != 'available' and max_trials > 0:
                status=filter(lambda x: x.id==volume.id, self.driver.list_volumes())[0].extra['state']
                time.sleep(10)
                max_trials -= 1

            self.driver.destroy_volume(volume)
    
        destroy_res = self.driver.destroy_node(libcloud_node)
        return destroy_res

    def create_volume(self, size, name, vm_id=None):
        # We can ignore vm_id. It is only needed by EC2.
        return self.driver.create_volume(size, name)

    def attach_volume(self, node, volume, device):
        return self.driver.attach_volume(node, volume, device)

    def detach_volume(self, volume):
        return self.driver.detach_volume(volume)

    def destroy_volume(self, volume):
        return self.driver.destroy_volume(volume)

    def list_instance_volumes(self, instance):
        raise NotImplementedError(
            'list_instance_volumes not implemented for this cloud driver')
