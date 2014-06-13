# -*- coding: utf-8 -*-

"""
    conpaas.core.clouds.dummy
    =========================

    ConPaaS core: Dummy cloud IaaS code.

    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from .base import Cloud


class HarnessCloud(Cloud):
    '''Support for "harness" clouds'''

    def __init__(self, cloud_name, iaas_config):
        Cloud.__init__(self, cloud_name)
        #TODO:(genc) put this on configurations
        self.url = "http://131.254.201.5:5558" 

    def get_cloud_type(self):
        return 'harness'

    def _connect(self):
        '''Connect to dummy cloud'''
        #DummyDriver = get_driver(Provider.DUMMY)
        #self.driver = DummyDriver(0)
        self.conn = httplib2.Http()
        self.connected = True

    def config(self, config_params={}, context=None):
        if context is not None:
            self._context = context

    def new_instances(self, count, name='conpaas', inst_type=None):
        raise Exception('Method not supported for this cloud')
        #if not self.connected:
            #self._connect()

        #return [self._create_service_nodes(self.driver.create_node(), False)
                #for _ in range(count)]

    def kill_instance(self, node):
        '''Kill a VM instance.

        @param node: A ServiceNode instance, where node.id is the vm_id
        '''
        raise Exception('Method not supported for this cloud')
        #if self.connected is False:
            #raise Exception('Not connected to cloud')

        ## destroy_node does not work properly in libcloud's dummy
        ## driver. Just return True.
        #return True
    
        #def __make_request(self, url, content = {}):
        ##print "Conn ID =", id(self)
        #print "\nRequest :",url
        #print content
        #data, response = self.cHonn.request(self.url + url , 'POST',
                          #simplejson.dumps(content),
                          #headers={'Content-Type': 'application/json'})
        #try:
            #response = simplejson.loads(response)
        #except:
            #print traceback.print_exc()
            #return response

        #print "Response :", response
        #return response


    def prepareReservation(self, configuration = {}):
        response = self.__make_request("/prepareReservation", configuration)
        return response

    def createReservation(self, configurationID):
        response = self.__make_request("/createReservation", {"configID" : configurationID})
        print response

        return response

    def releaseReservation(self, reservationID):
        response = self.__make_request("/releaseReservation", {"reservID" : reservationID})

        return response

    
    # def checkReservation(self, reservationID):
    #    response = self.__make_request("/checkReservation", {"reservID" : reservationID})
    #    return response
