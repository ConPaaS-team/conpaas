from threading import Thread

import subprocess
import time
import os.path

import simplejson
import ConfigParser
import StringIO
import sys


from conpaas.core.log import create_logger
from conpaas.core.expose import expose

from conpaas.core.controller import Controller

from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.https.server import HttpErrorResponse
from conpaas.core.https.server import FileUploadField
from conpaas.core.https.server import ConpaasRequestHandlerComponent

from conpaas.core.services import manager_services 
from conpaas.core.misc import file_get_contents

from conpaas.core.appmanager.core.patterns.store import Traces
from conpaas.core.appmanager.core.context.parser import ManifestParser, SLOParser
from conpaas.core.appmanager.profiler.profiler import Profiler
from conpaas.core import https
import urlparse

class ApplicationManager(ConpaasRequestHandlerComponent):

    def __init__(self, httpsserver, config_parser, **kwargs):
        ConpaasRequestHandlerComponent.__init__(self)
        self.logger = create_logger(__name__)
        self.httpsserver = httpsserver
        self.config_parser = config_parser

        #TODO:(genc): You might consider to remove the controller from the base manager and use only this one.
        #self.controller = Controller(config_parser)
        self.instance_id = 0
        self.kwargs = kwargs

        #TODO:(genc) Put some order in this parsing, it is horrible
        #sloconent = file_get_contents(kwargs['slo'])
        #self.slo = SLOParser.parse(simplejson.loads(sloconent))
        #self.application = ManifestParser.load(kwargs['manifest'])


        #for module in self.application.Modules:
        #    self.create_service(self, [{'service_type':module.ModuleType}])
            

        #self.run_am()

        #sys.stdout.flush()
    
    @expose('GET')
    def check_manager_process(self, kwargs):
        """Check if manager process started - just return an empty response"""
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        return HttpJsonResponse()    

    @expose('GET')
    def get_profiling_info(self, kwargs):
        return HttpJsonResponse(Traces.Experiments)    


    def run_am(self, cloud):
        if self.manifest.PerformanceModel == None:
            profiler = Profiler(self, cloud)
            profiler.run()
        sys.stdout.flush()


    
    # Details consist of resources(or devices), roles and distance
    def get_details_from_implementation(self, implementation):
        impl_resources = implementation.Resources
        
        details = {}
        details['Roles'] = impl_resources.Roles
        details['Resources'] = []
        for impl_device in impl_resources.Devices:
            device = {}
            device['GroupID'] = impl_device.GroupID
            device['Type'] = impl_device.Type
            device['NumInstances'] = impl_device.NumInstances.currentValue
            device['Role'] = impl_device.Role
            device['Attributes'] = {}
            for att_key in impl_device.Attributes.__dict__:
                device['Attributes'][att_key] = impl_device.Attributes.__dict__[att_key].currentValue
            details['Resources'].append(device)    
            
        return details

    @expose('UPLOAD')
    def upload_manifest_slo(self, kwargs):

        manifestfile = kwargs.pop('manifest')
        manifestconent = manifestfile.file
        self.manifest = ManifestParser.parse(simplejson.loads(manifestconent.read()))

        slofile = kwargs.pop('slo')
        sloconent = slofile.file
        self.slo = SLOParser.parse(simplejson.loads(sloconent.getvalue()))
        

        #Note that I am assuming that an application has only ONE generic service    
        self.app_tar = kwargs.pop('app_tar')
        #apptarfile = kwargs.pop('app_tar')
        #self.app_tar = apptarfile.file
        
        self.appid = kwargs.pop('appid')
        Thread(target=self.run_am, args=[kwargs['cloud']]).start()
        #self.run_am(kwargs['cloud'])

        # resc = {}
        # service_ids=[]
        # for module in self.manifest.Modules:
        #     #self.set_resource_variables(module.Implementations[0]):
        #     impl_detail = self.get_details_from_implementation(module.Implementations[0])
        #     res = self.create_service({'service_type':module.ModuleType})
        #     #check res for error and so on
        #     service_ids.append(res.obj['sid']) 
        #     service_manager = self.httpsserver.instances[int(res.obj['sid'])]
        #     resc['Resources'] = impl_detail['Resources']
        #     reservation = service_manager.controller.prepare_reservation(resc)
        #     #check cost reservation['Cost'] and contiune
        #     serv_resc = service_manager.controller.create_reservation_test(reservation['ConfigID'])    
        #     service_manager._do_startup(kwargs['cloud'], serv_resc)
        #     service_manager.controller.release_reservation(reservation['ConfigID'])
        
        
        return HttpJsonResponse({'success': True})
  
  
    @expose('POST')
    def create_service(self, kwargs):
        """Expose methods relative to a specific service manager"""
        self.kwargs.update(kwargs)

        if 'service_type' not in kwargs:
            vals = { 'arg': 'service_type' }
            return HttpErrorResponse('Argument %s is missing' % vals)

        service_type = kwargs.pop('service_type')
        services = manager_services

        try:
            module = __import__(services[service_type]['module'], globals(), locals(), ['*'])
        except ImportError:
            raise Exception('Could not import module containing service class "%(module)s"' % 
                services[service_type])

        # Get the appropriate class for this service
        service_class = services[service_type]['class']
        try:
            instance_class = getattr(module, service_class)
        except AttributeError:
            raise Exception('Could not get service class %s from module %s' % (service_class, module))

        self.add_manager_configuration(service_type)
        self.run_manager_start_script(service_type)
		

        #Create an instance of the service class
        #Watch the config parser is from the applciation manager and it is not specific, can be source for problems
        service_insance = instance_class(self.config_parser, **self.kwargs)
        
        #probably lock it 
        self.instance_id = self.instance_id + 1 
        
        self.httpsserver.instances[self.instance_id] = service_insance

        service_manager_exposed_functions = service_insance.get_exposed_methods()
        

        for http_method in service_manager_exposed_functions:
           for func_name in service_manager_exposed_functions[http_method]:
               self.httpsserver._register_method(http_method, self.instance_id, func_name, service_manager_exposed_functions[http_method][func_name])

        
       
        return HttpJsonResponse({'sid':self.instance_id})


    def add_manager_configuration(self, service_type):
        # Add service-specific config file (if any)
        conpaas_home = self.config_parser.get('manager', 'conpaas_home')
        mngr_cfg_dir = os.path.join(conpaas_home, 'config', 'manager')
        mngr_service_cfg = os.path.join(mngr_cfg_dir, service_type + '-manager.cfg')
        if os.path.isfile(mngr_service_cfg):
            self.config_parser.read(mngr_service_cfg)

            #TODO:(genc) get rid of static path 
            vars_cfg = os.path.join("/root", 'vars.cfg')
            ini_str = '[root]\n' + open(vars_cfg, 'r').read()
            ini_fp = StringIO.StringIO(ini_str)
            config = ConfigParser.RawConfigParser()
            config.readfp(ini_fp)
            
            # populate values refering to other values
            for key, value in self.config_parser.items('manager'):
                if value.startswith('%') and value.endswith('%'):
                    self.config_parser.set('manager', key, config.get('root', value.strip('%').lower()))



    def run_manager_start_script(self, service_type):
        #before running the manager script get again the variable values from the context
        conpaas_home = self.config_parser.get('manager', 'conpaas_home')
        mngr_scripts_dir = os.path.join(conpaas_home, 'scripts', 'manager')
        mngr_startup_scriptname = os.path.join(mngr_scripts_dir, service_type + '-manager-start')          
        if os.path.isfile(mngr_startup_scriptname):
            proc = subprocess.Popen(['bash', mngr_startup_scriptname] , close_fds=True)
            proc.wait()
    

    def dir_create_service(self, service_type, sid):
        try:
            parsed_url = urlparse.urlparse(self.config_parser.get('manager', 'START_URL'))
            _, body = https.client.https_post(parsed_url.hostname,
                                              parsed_url.port or 443,
                                              parsed_url.path,
                                              params={'service_type': service_type, 'appid':self.appid, 'sid':sid})
                                              
            obj = simplejson.loads(body)
            return not obj['error']
        except:
            #self.__logger.exception('Failed to deduct credit')
            return False    