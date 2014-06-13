from threading import Thread

import subprocess
import time
import os.path

import ConfigParser
import StringIO

from conpaas.core.log import create_logger
from conpaas.core.expose import expose


from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.https.server import HttpErrorResponse
from conpaas.core.https.server import FileUploadField
from conpaas.core.https.server import ConpaasRequestHandlerComponent

from conpaas.core.services import manager_services 

class ApplicationManager(ConpaasRequestHandlerComponent):

    def __init__(self, httpsserver, config_parser, **kwargs):
        ConpaasRequestHandlerComponent.__init__(self)
        self.logger = create_logger(__name__)
        self.httpsserver = httpsserver
        self.config_parser = config_parser
        self.instance_id = 0
        self.kwargs = kwargs



    @expose('POST')
    def create_service(self, kwargs):
        """Expose methods relative to a specific service manager"""

        if 'service_type' not in kwargs:
            vals = { 'arg': 'service_type' }
            return HttpErrorResponse(self.REQUIRED_ARG_MSG % vals)

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
        proc = subprocess.Popen(['bash', mngr_startup_scriptname] , close_fds=True)
        proc.wait()
        