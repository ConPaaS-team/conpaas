from threading import Thread

import subprocess
import time
import os.path

import simplejson
import ConfigParser
import StringIO
import sys, tempfile


from conpaas.core.log import create_logger
from conpaas.core.expose import expose

from conpaas.core.controller import Controller
from conpaas.core.manager import ManagerException

from conpaas.core.https.server import HttpJsonResponse
from conpaas.core.https.server import HttpErrorResponse
from conpaas.core.https.server import FileUploadField
from conpaas.core.https.server import ConpaasRequestHandlerComponent

from conpaas.core.services import manager_services 
from conpaas.core.misc import file_get_contents

from conpaas.core.appmanager.core.patterns.store import Traces
from conpaas.core.appmanager.core.context.parser import ManifestParser
from conpaas.core.appmanager.slo import User, Objectives, SLOParser
from conpaas.core.appmanager.profiler.profiler import Profiler
from conpaas.core.appmanager.selection import SLOEnforcer
from conpaas.core import https
import urlparse

from conpaas.core.misc import archive_open, archive_get_members, archive_close, archive_get_type, archive_extract_file
from conpaas.core.misc import CodeVersion, ServiceConfiguration

class ApplicationManager(ConpaasRequestHandlerComponent):

    S_INIT = 'INIT'         # manager initialized but not yet started
    S_PROLOGUE = 'PROLOGUE' # manager is starting up
    S_RUNNING = 'RUNNING'   # manager is running
    S_ADAPTING = 'ADAPTING' # manager is in a transient state - frontend will 
                            # keep polling until manager out of transient state
    S_PROFILING = 'PROFILING'  
    S_EPILOGUE = 'EPILOGUE' # manager is shutting down
    S_STOPPED = 'STOPPED'   # manager stopped
    S_ERROR = 'ERROR'       # manager is in error state


    def __init__(self, httpsserver, config_parser, **kwargs):
        self.state = self.S_INIT
        ConpaasRequestHandlerComponent.__init__(self)
        self.logger = create_logger(__name__)
        self.httpsserver = httpsserver
        self.config_parser = config_parser
        self.cache = config_parser.get('manager', 'VAR_CACHE')
        self.performance_model = {'experiments':{}, 'pareto':[]}

        self.code_repo = config_parser.get('manager', 'CODE_REPO')

        #TODO:(genc): You might consider to remove the controller from the base manager and use only this one.
        #self.controller = Controller(config_parser)
        self.instance_id = 0
        self.kwargs = kwargs
        self.state = self.S_RUNNING

        self.module_managers = []
        self.execinfo = {}
        self.app_tar = None

        self.config = ServiceConfiguration()
        self.debug = 0

        #TODO:(genc) Put some order in this parsing, it is horrible
        #sloconent = file_get_contents(kwargs['slo'])
        #self.slo = SLOParser.parse(simplejson.loads(sloconent))
        #self.application = ManifestParser.load(kwargs['manifest'])


        #for module in self.application.Modules:
        #    self.create_service(self, [{'service_type':module.ModuleType}])
            

        #self.run_am()

        #sys.stdout.flush()
        self.logger.info('The application manager was started')
    
    @expose('GET')
    def check_manager_process(self, kwargs):
        """Check if manager process started - just return an empty response"""
        if len(kwargs) != 0:
            return HttpErrorResponse('ERROR: Arguments unexpected')
        return HttpJsonResponse()    

    @expose('GET')
    def execute_slo(self, kwargs):
        Thread(target=self.execute_application_slo, args=[]).start()
        # execution_time, total_cost = self.execute_application_slo()

        return HttpJsonResponse({"success":True})
        # return HttpJsonResponse({"execution_time":execution_time, "total_cost":total_cost})    

    @expose('GET')
    def get_profiling_info(self, kwargs):
        download = kwargs.pop('download')
        # return HttpJsonResponse({'state':self.state, 'profile':{'experiments': Traces.Experiments, 'pareto':Traces.ParetoExperiments}})    
        app = True if self.app_tar else False
        return HttpJsonResponse({'state':self.state, 'pm': self.perparePerformanceModel(download), 'application':app, 'services':self.service_ids})    

    @expose('GET')
    def infoapp(self, kwargs):
        info = {}
        for i in range(len(self.manifest.Modules)):
            info[self.manifest.Modules[i].ModuleType] = self.module_managers[i].get_info()
        
        return HttpJsonResponse({'servinfo':info, 'execinfo': self.execinfo, 'frontend':self.frontend})    

    @expose('UPLOAD')
    def upload_profile(self, kwargs):
        profile = kwargs.pop('profile')
        profile = profile.file.read()
        self.performance_model = simplejson.loads(profile)
        # return HttpJsonResponse({'state':self.state, 'profile':{'experiments': Traces.Experiments, 'pareto':Traces.ParetoExperiments}})    
        return HttpJsonResponse({'len':len(profile)})    


    @expose('UPLOAD')
    def upload_slo(self, kwargs):
        slofile = kwargs.pop('slofile')
        slofile = slofile.file.read()
        self.slo = SLOParser.parse(simplejson.loads(slofile))
        self.perparePerformanceModel(True)
        User.Objectives = self.slo.Objective
        self.sloconf = self.slomanager.select_configuration(User.Objectives, self.performance_model['pareto'])
        # return HttpJsonResponse({'state':self.state, 'profile':{'experiments': Traces.Experiments, 'pareto':Traces.ParetoExperiments}})    
        return HttpJsonResponse({'conf':self.sloconf})    

    def run_am(self):
        if self.manifest.PerformanceModel == None:
            self.state = self.S_PROFILING
            profiler = Profiler(self)
            profiler.run()
            # self.performance_model['experiments'] = profiler.run()

            self.state = self.S_RUNNING
            self.perparePerformanceModel(True)
        sys.stdout.flush()

    def execute_application_slo(self):
        implementation = None
        #genc: again taking the only module here
        for impl in self.manifest.Modules[0].Implementations:
            if impl.ImplementationID == self.sloconf['ImplementationID']:
                implementation = impl
                break

        configuration, roles = implementation.Resources.get_configuration(self.sloconf['Configuration'])
        reservation = self.reserve_resources(configuration)
        for i in range(len(reservation['Instances'])):
           reservation['Instances'][i]["Role"] = roles[i]
        execution_time, total_cost = self.execute_application(reservation, self.sloconf['Arguments'], False)
        self.execinfo = {"execution_time":execution_time, "total_cost":total_cost}


    def execute_application(self, reservation, args, profiling):
        #for now we use only one module, has to be updated when using multiple modules
        module_manager = self.module_managers[0]
        print "execute_application: reserv: %s, args: %s" % (reservation, args)
        self.frontend = module_manager._do_startup({'cloud':self.cloud, 'configuration':reservation, 'args': args, 'code_conf':self.config})
        
        # self.logger.info("actually came out of do startup")

        "Execute implementation"
        start_time = time.time()
        module_manager._do_run(profiling, args)
        end_time = time.time()
        execution_time = end_time - start_time
        execution_time = execution_time / 60
        total_cost = execution_time * reservation["Cost"]

        if not self.debug:
            module_manager.cleanup_agents()
            module_manager.controller.release_reservation(reservation['ConfigID'])

        # return round(execution_time, 4), round(total_cost, 4)
        return execution_time, total_cost

    def reserve_resources(self, configuration):
        #for now we use only one module, has to be updated when using multiple modules
        module_manager = self.module_managers[0]
        reservation = module_manager.controller.prepare_reservation(configuration)
        #check cost reservation['Cost'] and contiune
        #cost = reservation['Cost']
        reservation = module_manager.controller.create_reservation_test(reservation, module_manager.get_check_agent_funct(), 5555)
        return reservation
    
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
    def upload_manifest(self, kwargs):

        manifestfile = kwargs.pop('manifest')
        manifestconent = manifestfile.file
        self.manifest_json = manifestconent.read();
        self.manifest = ManifestParser.parse(simplejson.loads(self.manifest_json))
        self.slomanager = SLOEnforcer(self.manifest)
        # slofile = kwargs.pop('slo')
        # sloconent = slofile.file
        # self.slo = SLOParser.parse(simplejson.loads(sloconent.getvalue()))
        

        #Note that I am assuming that an application has only ONE generic service    
        # self.app_tar = kwargs.pop('app_tar')
        self.service_ids = {}
        self.implementationsXmodule = []

        for i in range(len(self.manifest.Modules)):
            self.implementationsXmodule.append(len(self.manifest.Modules[i].Implementations) - 1) 
            res = self.create_service({'service_type':self.manifest.Modules[i].ModuleType})
            self.dir_create_service(self.manifest.Modules[i].ModuleType, res.obj['sid'])
            self.service_ids[res.obj['sid']] = self.httpsserver.instances[int(res.obj['sid'])].get_type()
            # self.module_managers.append(self.appmanager.httpsserver.instances[int(res.obj['sid'])]) 
        
        self.appid = kwargs.pop('appid')
        self.cloud = kwargs['cloud']
        
        # Thread(target=self.run_am, args=[]).start()
        #self.run_am()

        return HttpJsonResponse({'sids': self.service_ids})
    
    @expose('GET')
    def download_manifest(self, kwargs):
        return HttpJsonResponse({'manifest': self.manifest_json}) 


    @expose('GET')
    def profile(self, kwargs):
        iterations = kwargs.pop('iterations')
        debug = kwargs.pop('debug')
        self.iterations = iterations
        self.debug = int(debug)
        Thread(target=self.run_am, args=[]).start()
        return HttpJsonResponse({'success': True})
        
    def perparePerformanceModel(self, download):
        flat_pm = {'experiments':[], 'pareto':[]}
        for impl in self.performance_model['experiments']:
            for i in range(len(self.performance_model['experiments'][impl])):
                self.performance_model['experiments'][impl][i]['ImplementationID'] = impl
            flat_pm['experiments'].extend(self.performance_model['experiments'][impl])        

        if self.state == self.S_RUNNING:
            flat_pm['pareto'] = self.slomanager.get_pareto_experiments(flat_pm['experiments'])
            if download:
                if len(self.performance_model['pareto']) == 0:
                    self.performance_model['pareto'] = flat_pm['pareto']
                return self.performance_model
        if download and self.state != self.S_RUNNING:
            return {}

        return flat_pm

    def add_experiment(self, experiment):
        if experiment['ImplementationID'] not in self.performance_model['experiments']:
            self.performance_model['experiments'][experiment['ImplementationID']] = []
        self.performance_model['experiments'][experiment['ImplementationID']].append(experiment)
  
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
		
        #probably lock it 
        self.instance_id = self.instance_id + 1 
        self.kwargs.update({'service_id':self.instance_id})
        #Create an instance of the service class
        #Watch the config parser is from the applciation manager and it is not specific, can be source for problems
        service_insance = instance_class(self.config_parser, **self.kwargs)
        
        
        
        self.httpsserver.instances[self.instance_id] = service_insance
        self.module_managers.append(service_insance)

        service_manager_exposed_functions = service_insance.get_exposed_methods()
        

        for http_method in service_manager_exposed_functions:
           for func_name in service_manager_exposed_functions[http_method]:
               self.httpsserver._register_method(http_method, self.instance_id, func_name, service_manager_exposed_functions[http_method][func_name])

        
       
        return HttpJsonResponse({'sid':self.instance_id})


    @expose('UPLOAD')
    def upload_application(self, kwargs):
        if 'appfile' not in kwargs:
            ex = ManagerException(ManagerException.E_ARGS_MISSING, 'appfile')
            return HttpErrorResponse(ex.message)
        code = kwargs.pop('appfile')
        
        self.app_tar = code
        
        if 'description' in kwargs:
            description = kwargs.pop('description')
        else:
            description = ''
        
        if 'enable' in kwargs:
            enable = kwargs.pop('enable')
        else:
            enable = False

        if 'service_id' in kwargs:
            service_id = kwargs.pop('service_id')

        if len(kwargs) != 0:
            ex = ManagerException(ManagerException.E_ARGS_UNEXPECTED,
                                  kwargs.keys())
            return HttpErrorResponse(ex.message)
        if not isinstance(code, FileUploadField):
            ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                  detail='codeVersionId should be a file')
            return HttpErrorResponse(ex.message)

        
        path = self.code_repo + '/' + service_id
        if not os.path.exists(path):
            os.makedirs(path)
        fd, name = tempfile.mkstemp(prefix='app-', dir=path)
        fd = os.fdopen(fd, 'w')
        upload = code.file
        codeVersionId = os.path.basename(name)
        self.logger.info("upload is an instance of %s" % upload)

        bytes = upload.read(2048)
        # self.logger.info("byte has len: %s" % len(bytes))
        while len(bytes) != 0:
            fd.write(bytes)
            bytes = upload.read(2048)
            # self.logger.info("byte has len: %s" % len(bytes))
        fd.close()

        arch = archive_open(name)
        if arch is None:
            #os.remove(name)
            ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                  detail='Invalid archive format')
            return HttpErrorResponse(ex.message)

        for fname in archive_get_members(arch):
            if fname.startswith('/') or fname.startswith('..'):
                archive_close(arch)
                os.remove(name)
                ex = ManagerException(ManagerException.E_ARGS_INVALID,
                                      detail='Absolute file names are not allowed in archive members')
                return HttpErrorResponse(ex.message)
        archive_close(arch)
        self.config.codeVersions[codeVersionId] = CodeVersion(
            codeVersionId, os.path.basename(code.filename), archive_get_type(name),name, description=description)

        if enable:
            self.do_enable_code(os.path.basename(codeVersionId))

        return HttpJsonResponse({'codeVersionId': os.path.basename(codeVersionId)})
    

    @expose('POST')                                                                                      
    def enable_code(self, kwargs):                                                          
        codeVersionId = None
        if 'codeVersionId' in kwargs:
            codeVersionId = kwargs.pop('codeVersionId')                                                  
        
        phpconf = {}                                                                                     
                                                                                                         
        if len(kwargs) != 0:                                                                             
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys()).message)                                                                                                 
                                                                                                         
        if codeVersionId is None:                                                        
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_MISSING, '"codeVersionId" is not specified').message)                                                                   
                                                                                                         
        if codeVersionId and codeVersionId not in self.config.codeVersions:                                   
            return HttpErrorResponse(ManagerException(ManagerException.E_ARGS_INVALID, detail='Unknown code version identifier "%s"' % codeVersionId).message)                                                    
                                                                                                         
                                                                             
        if self.state == self.S_INIT or self.state == self.S_STOPPED:                                            
            if codeVersionId:                                                                            
                self.config.currentCodeVersion = codeVersionId                                                
            
        elif self.state == self.S_RUNNING:                                                                   
            self.state = self.S_ADAPTING
            Thread(target=self.do_enable_code, args=[codeVersionId]).start()   
        else:                                                                                            
            return HttpErrorResponse(ManagerException(ManagerException.E_STATE_ERROR).message)           
        return HttpJsonResponse()                                                                        

    def do_enable_code(self, codeVersionId):    
        if codeVersionId is not None:                                     
            self.config.currentCodeVersion = codeVersionId                     
            #self._update_code(config, self.nodes)       
        self.state = self.S_RUNNING
        
    @expose('GET')
    def list_code_versions(self, kwargs):
        if len(kwargs) != 0:
            ex = ManagerException(ManagerException.E_ARGS_UNEXPECTED, kwargs.keys())
            return HttpErrorResponse(ex.message)
        
        versions = []
        for version in self.config.codeVersions.values():
            item = {'codeVersionId': version.id, 'filename': version.filename,
                    'description': version.description, 'time': version.timestamp}
            if version.id == self.config.currentCodeVersion:
                item['current'] = True
            versions.append(item)
        versions.sort(cmp=(lambda x, y: cmp(x['time'], y['time'])), reverse=True)
        return HttpJsonResponse({'codeVersions': versions})


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
                                              params={'service_type': service_type, 'appid':self.config_parser.get('manager', 'APP_ID'), 'sid':sid})
            obj = simplejson.loads(body)
            return not obj['error']
        except:
            #self.__logger.exception('Failed to deduct credit')
            return False    

    # def save_profile(self):
    #     f=open(os.path.join(self.cache, 'profile'), 'a')
    #     f.write("{ 'experiments': %s, \n" % Traces.TrainingSet)
    #     f.write("'pareto': %s\n }" % Traces.ParetoExperiments)
    #     f.close()