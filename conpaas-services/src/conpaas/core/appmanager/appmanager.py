from threading import Thread

import subprocess
import time
import os.path

import simplejson
import ConfigParser
import StringIO
import sys, tempfile, traceback


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

from conpaas.core.appmanager.specification.manifest import ManifestParser
from conpaas.core.appmanager.specification.slo import SLOParser


# from conpaas.core.appmanager.profiler.profiler import Profiler
# from conpaas.core.appmanager.selection import SLOEnforcer
from conpaas.core import https
import urlparse

from conpaas.core.misc import archive_open, archive_get_members, archive_close, archive_get_type, archive_extract_file
from conpaas.core.misc import CodeVersion, ServiceConfiguration

from conpaas.core.appmanager.state import State
from conpaas.core.appmanager.application.search_space import VariableMapper
from conpaas.core.appmanager.profiler.profiler import Profiler
from conpaas.core.appmanager.modeller.extrapolator import Extrapolator
from conpaas.core.appmanager.selection import SLOEnforcer
from conpaas.core.appmanager.executor import Executor

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
        # self.performance_model = {'experiments':{}, 'extrapolations':{}, 'pareto':[]}
        # self.performance_model = {'experiments':[], 'extrapolations':[], 'pareto':[], 'failed':[]}
        self.performance_model = {'experiments':[], 'extrapolations':[], 'pareto':[]}

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
        self.frontend=''

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
        if not self.sloconf or len(self.sloconf) == 0:
            return HttpJsonResponse({"success":True, "error": "No configuration selected"})            
        
        Thread(target=self.execute_application_slo, args=[]).start()
        # execution_time, total_cost = self.execute_application_slo()

        return HttpJsonResponse({"success":True})
        # return HttpJsonResponse({"execution_time":execution_time, "total_cost":total_cost})    

    @expose('GET')
    def get_profiling_info(self, kwargs):
        download = kwargs.pop('download')
        # return HttpJsonResponse({'state':self.state, 'profile':{'experiments': Traces.Experiments, 'pareto':Traces.ParetoExperiments}})    
        app = True if self.app_tar else False
        return HttpJsonResponse({'state':self.state, 'pm': self.preparePerformanceModel(download), 'application':app, 'services':self.service_ids})    

    @expose('GET')
    def infoapp(self, kwargs):
        info = {}
        for i in range(len(self.application.Modules)):
            info[self.application.Modules[i].ModuleType] = self.module_managers[i].get_info()
        
        return HttpJsonResponse({'servinfo':info, 'execinfo': self.execinfo, 'frontend':self.frontend})    

    @expose('UPLOAD')
    def upload_profile(self, kwargs):
        profile = kwargs.pop('profile')
        profile = profile.file.read()
        self.logger.debug(profile)
        self.performance_model = simplejson.loads(profile)
        # return HttpJsonResponse({'state':self.state, 'profile':{'experiments': Traces.Experiments, 'pareto':Traces.ParetoExperiments}})    
        return HttpJsonResponse({'len':len(profile)})    


    @expose('UPLOAD')
    def upload_slo(self, kwargs):
        slofile = kwargs.pop('slofile')
        slofile = slofile.file.read()
        self.logger.info("slo from web: %s" % slofile)        
        self.slo = SLOParser.parse(simplejson.loads(slofile))
        self.enforcer.set_slo(self.slo)

        # self.logger.info("slo file: %s" % self.slo)
        # self.preparePerformanceModel(True)
        # User.Objectives = self.slo.Objective
        self.sloconf = self.enforcer.select_valid_configurations(self.performance_model['pareto'])
        # return HttpJsonResponse({'state':self.state, 'profile':{'experiments': Traces.Experiments, 'pareto':Traces.ParetoExperiments}})    
        


        return HttpJsonResponse({'conf':self.sloconf})    
        # return HttpJsonResponse({'conf':'lesh'})    

    # def run_am(self):
    #     if self.manifest.PerformanceModel == None:
    #         self.state = self.S_PROFILING
    #         profiler = Profiler(self)
    #         profiler.run()
    #         # self.performance_model['experiments'] = profiler.run()

    #         self.state = self.S_RUNNING
    #         self.preparePerformanceModel(True)
    #     sys.stdout.flush()

    def execute_application_slo(self):
        
        exp = self.sloconf[0]
        result = Executor.execute_on_configuration(self.application, exp['Implementations'], exp['ConfVars'].keys(), exp['ConfVars'], exp['Parameters'])
        # implementation = None
        # #genc: again taking the only module here
        # for impl in self.manifest.Modules[0].Implementations:
        #     if impl.ImplementationID == self.sloconf['ImplementationID']:
        #         implementation = impl
        #         break

        # configuration, roles = implementation.Resources.get_configuration(self.sloconf['Configuration'])
        # reservation = self.reserve_resources(configuration)
        # for i in range(len(reservation['Instances'])):
        #    reservation['Instances'][i]["Role"] = roles[i]
        # execution_time, total_cost = self.execute_application(reservation, self.sloconf['Arguments'], False)
        self.execinfo = {"execution_time":result[3], "total_cost":result[2]}


    # def execute_application_old(self, reservation, args, profiling):
    #     #for now we use only one module, has to be updated when using multiple modules
    #     module_manager = self.module_managers[0]
    #     print "execute_application: reserv: %s, args: %s" % (reservation, args)
    #     self.frontend = module_manager._do_startup({'cloud':self.cloud, 'configuration':reservation, 'args': args, 'code_conf':self.config})
        
    #     # self.logger.info("actually came out of do startup")

    #     "Execute implementation"
    #     start_time = time.time()
    #     module_manager._do_run(profiling, args)
    #     end_time = time.time()
    #     execution_time = end_time - start_time
    #     execution_time = execution_time / 60
    #     total_cost = execution_time * reservation["Cost"]

    #     if not self.debug:
    #         module_manager.cleanup_agents()
    #         module_manager.controller.release_reservation(reservation['ConfigID'])

    #     # return round(execution_time, 4), round(total_cost, 4)
    #     return execution_time, total_cost


    # def execute_application(self, reservation, args, profiling):
    #     #for now we use only one module, has to be updated when using multiple modules
    #     module_manager = self.module_managers[0]
    #     print "execute_application: reserv: %s, args: %s" % (reservation, args)
    #     self.frontend = module_manager._do_startup({'cloud':self.cloud, 'configuration':reservation, 'args': args, 'code_conf':self.config})
        
    #     # self.logger.info("actually came out of do startup")

    #     "Execute implementation"
    #     start_time = time.time()
    #     module_manager._do_run(profiling, args)
    #     end_time = time.time()
    #     execution_time = end_time - start_time
    #     execution_time = execution_time / 60
    #     total_cost = execution_time * reservation["Cost"]

    #     if not self.debug:
    #         module_manager.cleanup_agents()
    #         module_manager.controller.release_reservation(reservation['ConfigID'])

    #     # return round(execution_time, 4), round(total_cost, 4)
    #     return execution_time, total_cost

    def reserve_resources(self, configuration, constraints,  monitor):
        #for now we use only one module, has to be updated when using multiple modules
        module_manager = self.module_managers[0]
        # reservation = module_manager.controller.prepare_reservation(configuration)
        #check cost reservation['Cost'] and contiune
        #cost = reservation['Cost']
        if self.monitor:
            reservation = module_manager.controller.create_reservation_test(configuration, module_manager.get_check_agent_funct(), 5555, constraints, monitor)
        else:
            self.monitor_target = monitor
            reservation = module_manager.controller.create_reservation_test(configuration, module_manager.get_check_agent_funct(), 5555, constraints, monitor) 
        return reservation
   
    def release_resources(self, reservationID):
        module_manager = self.module_managers[0]
        # module_manager.cleanup_agents()
        self.logger.debug("calling release_reservation")
        if not self.debug:
            module_manager.controller.release_reservation(reservationID)

    def get_cost(self, configuration, constraints):
        module_manager = self.module_managers[0]
        return module_manager.controller.get_cost(configuration, constraints)

    def get_monitoring(self, reservationID, address):
        module_manager = self.module_managers[0]
        
        if self.monitor:
            # mon_info = module_manager.controller.monitor(reservationID, address)
            mon_info = {'CPU_U_S_TIME': '1,1443617808.0,3.0\n2,1443617809.0,19.0\n3,1443617812.0,47.0\n4,1443617813.0,81.0\n5,1443617814.0,112.0\n6,1443617815.0,144.0\n7,1443617817.0,155.0\n8,1443617818.0,155.0\n9,1443617819.0,155.0\n10,1443617820.0,155.0\n11,1443617822.0,166.0\n12,1443617823.0,167.0\n13,1443617824.0,167.0\n14,1443617825.0,167.0\n15,1443617826.0,167.0\n16,1443617827.0,167.0\n17,1443617828.0,167.0\n18,1443617829.0,167.0\n19,1443617830.0,167.0\n20,1443617831.0,167.0\n', 'MEM_U_S_BYTE': '1,1443617808.0,8470528.0\n2,1443617810.0,25010176.0\n3,1443617812.0,23830528.0\n4,1443617813.0,28930048.0\n5,1443617814.0,35192832.0\n6,1443617815.0,33308672.0\n7,1443617817.0,25001984.0\n8,1443617818.0,23670784.0\n9,1443617819.0,23670784.0\n10,1443617820.0,19755008.0\n11,1443617822.0,25112576.0\n12,1443617823.0,23588864.0\n13,1443617824.0,21438464.0\n14,1443617825.0,21049344.0\n15,1443617826.0,20688896.0\n16,1443617827.0,20471808.0\n17,1443617828.0,20471808.0\n18,1443617829.0,19812352.0\n19,1443617830.0,19812352.0\n20,1443617831.0,19812352.0\n', 'MEM_TOT_BYTE': '1,1443617808.0,1073741824.0\n2,1443617810.0,1073741824.0\n3,1443617812.0,1073741824.0\n4,1443617813.0,1073741824.0\n5,1443617814.0,1073741824.0\n6,1443617815.0,1073741824.0\n7,1443617817.0,1073741824.0\n8,1443617818.0,1073741824.0\n9,1443617819.0,1073741824.0\n10,1443617820.0,1073741824.0\n11,1443617822.0,1073741824.0\n12,1443617823.0,1073741824.0\n13,1443617824.0,1073741824.0\n14,1443617825.0,1073741824.0\n15,1443617826.0,1073741824.0\n16,1443617827.0,1073741824.0\n17,1443617828.0,1073741824.0\n18,1443617829.0,1073741824.0\n19,1443617830.0,1073741824.0\n20,1443617831.0,1073741824.0\n', 'CPU_TOT_TIME': '1,1443617808.0,6817940.0\n2,1443617810.0,6818108.0\n3,1443617812.0,6818273.0\n4,1443617813.0,6818383.0\n5,1443617814.0,6818493.0\n6,1443617815.0,6818630.0\n7,1443617817.0,6818747.0\n8,1443617818.0,6818890.0\n9,1443617819.0,6818988.0\n10,1443617820.0,6819100.0\n11,1443617822.0,6819197.0\n12,1443617823.0,6819294.0\n13,1443617824.0,6819390.0\n14,1443617825.0,6819485.0\n15,1443617826.0,6819581.0\n16,1443617827.0,6819684.0\n17,1443617828.0,6819778.0\n18,1443617829.0,6819878.0\n19,1443617830.0,6819981.0\n20,1443617831.0,6820080.0\n'}
        else:
            mon_info={}
            for tp in self.monitor_target:
                if tp != "PollTime":
                    for metr in self.monitor_target[tp]:
                        mon_info[metr] = ''

        # self.logger.info('###MONITOR###: %s' % mon_info)
        return mon_info
        

    # Details consist of resources(or devices), roles and distance
    def get_details_from_implementation(self, implementation):
        impl_resources = implementation.Resources
        
        details = {}
        details['Roles'] = impl_resources.Roles
        details['Resources'] = []
        for impl_device in impl_resources.Devices:
            device = {}
            device['Group'] = impl_device.Group
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
        self.application = ManifestParser.parse(self.manifest_json)
        self.application.manager = self 
        self.versions = self.application.generate_app_versions()
        # self.slomanager = SLOEnforcer(self.manifest)
        self.enforcer = SLOEnforcer(self.application, self.versions)

        # slofile = kwargs.pop('slo')
        # sloconent = slofile.file
        # self.slo = SLOParser.parse(simplejson.loads(sloconent.getvalue()))
        

        #Note that I am assuming that an application has only ONE generic service    
        # self.app_tar = kwargs.pop('app_tar')
        self.service_ids = {}
        self.implementationsXmodule = []

        for i in range(len(self.application.Modules)):
            self.implementationsXmodule.append(len(self.application.Modules[i].Implementations) - 1) 
            res = self.create_service({'service_type':self.application.Modules[i].ModuleType})
            self.dir_create_service(self.application.Modules[i].ModuleType, res.obj['sid'])
            self.service_ids[res.obj['sid']] = self.httpsserver.instances[int(res.obj['sid'])].get_type()
            # self.module_managers.append(self.appmanager.httpsserver.instances[int(res.obj['sid'])]) 
        
        self.appid = kwargs.pop('appid')
        self.cloud = kwargs['cloud']
        
        self.logger.info("module managers: %s" % self.module_managers)

        # Thread(target=self.run_am, args=[]).start()
        #self.run_am()

        return HttpJsonResponse({'sids': self.service_ids})
    
    def run_profiling(self):
        self.state = self.S_PROFILING
        done, models = self.model_application()
        self.logger.info("Modelling done?: %s" % done)
        if done:            
            self.state = self.S_RUNNING
            # self.preparePerformanceModel(True)
            # self.enforcer.set_models(models)
        #     #application model has been built; enforce slo
        #     enforcer = SLOEnforcer(Controller.application, Controller.slo, Controller.versions, models)
        #     print "Enforce objective ..."
        #     result = enforcer.execute_application()
        #     print "Achievement (+ for slower/more expensive than predicted, - for faster/cheaper  than predicted) : ET = ", result[0], " COST = ", result[1]
            
        # print "Bye!"

    def model_application(self):
        #we can run the modelling in parallel for each version
        q = True 
        models = {}
        for v in self.versions:
            # self.logger.info("Version: %s" % v)
            done, model = self.model_version(v)
            models[".".join(map(lambda s: str(s), v))] = model
            q = q and done 
        
        return q, models


    # @staticmethod
    def model_version(self, v):
        version = ".".join(map(lambda s: str(s), v))
        #LOOK FOR PROFILE DATA
        profile_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "../profiles"))
        data_file = "%s/%s-%s.pf" % (profile_dir, self.application.Name, version)
        
        State.load(version, data_file)
        
        current_state = State.get_current_state(version)
        # self.logger.info("current_state: %s" % current_state)
    
        if current_state == 0:
            print "Profiling state."
            #profiling with static input phase
            #get the first small input size to profile with
            
            #if pure blackbox use the big size
            if self.extrapolate:
                parameters = VariableMapper(self.application.getParameterVariableMap()).lower_bound_values()
            else:
                parameters = self.application.getExecutionParameters(self.application.ExtrapolationArgs)

            #start profiler to create a model
            Profiler.StateID = current_state
            self.logger.info("parameters: %s" % parameters)
            profiler = Profiler(self.application, version, parameters = parameters)
            try:
                profiler.run()
            except:
                traceback.print_exc()
                print 'Profiler interrupted. Exiting'
                return False, None
            State.change_state(version)
            current_state = State.get_current_state(version)
            State.checkpoint(version, current_state)
            
        if not self.extrapolate:    
            return True, None
        #get the input size from the SLO for which to make prediction
        # input_size = self.application.getExecutionParameters(self.slo.ExecutionArguments)
        input_size = self.application.getExecutionParameters(self.application.ExtrapolationArgs)
        self.logger.info("input_size: %s" % input_size)
        modeller = None
        if current_state >= 1:
            print "Modelling state."
            #profiling variable input
            #modelling state - use function to predict
            Extrapolator.StateID = current_state
            # variables, solutions_identified_in_profiling = Profiler(self.application, version).get_explored_solutions()
            variables, solutions_identified_in_profiling, constraints = Profiler(self.application, version).get_explored_solutions()
            print len(solutions_identified_in_profiling)
            
            modeller = Extrapolator(self.application, version, variables, solutions_identified_in_profiling, input_size)
            try:
                modeller.run()
            except:
                traceback.print_exc()
                print 'Modeller interrupted. Exiting'
                return False, None
            State.change_state(version)
            current_state = State.get_current_state(version)

        print "Current state", current_state
        State.save(version)
        #retrieve the model - tuple (function,constraints)
        model = modeller.get_model() 
        return True, model
        # return True, None

    @expose('GET')
    def download_manifest(self, kwargs):
        return HttpJsonResponse({'manifest': self.manifest_json}) 


    @expose('GET')
    def profile(self, kwargs):
        iterations = kwargs.pop('iterations')
        debug = kwargs.pop('debug')
        monitor = kwargs.pop('monitor')
        extrapolate = kwargs.pop('extrapolate')
        self.iterations = int(iterations)
        self.debug = int(debug)
        self.monitor = int(monitor)
        self.extrapolate = int(extrapolate)
        self.logger.debug("extrapolate: %s, iterations: %s, debug: %s" % (self.extrapolate, self.iterations, self.debug))
        # Thread(target=self.run_am, args=[]).start()
        Thread(target=self.run_profiling, args=[]).start()

        # done, models = self.model_application()
        return HttpJsonResponse({'success': True})
        
    # def preparePerformanceModel(self, download):
    #     flat_pm = {'experiments':[],'extrapolations':[], 'pareto':[]}
    #     self.logger.debug("dowonload: %s, performance_model: %s" % (download, self.performance_model))

    #     for impl in self.performance_model['experiments']:
    #         # for i in range(len(self.performance_model['experiments'][impl])):
    #         #     self.performance_model['experiments'][impl][i]['ImplementationID'] = impl
    #         flat_pm['experiments'].extend(self.performance_model['experiments'][impl])        

    #     for impl in self.performance_model['extrapolations']:
    #         # for i in range(len(self.performance_model['extrapolations'][impl])):
    #         #     self.performance_model['extrapolations'][impl][i]['ImplementationID'] = impl
    #         flat_pm['extrapolations'].extend(self.performance_model['extrapolations'][impl])        

    #     if self.state == self.S_RUNNING:
    #         if len(flat_pm['experiments']) > 0:
    #             # self.logger.debug("experiments: %s" % flat_pm['experiments'])
    #             flat_pm['pareto'] = self.enforcer.get_pareto_experiments(flat_pm['experiments'])
    #         if download:
    #             if len(self.performance_model['pareto']) == 0:
    #                 self.performance_model['pareto'] = flat_pm['pareto']
    #             self.logger.debug("performance_model before download: %s" % self.performance_model)
    #             return self.performance_model
    #     if download and self.state != self.S_RUNNING:
    #         return {}

    #     return flat_pm


    def preparePerformanceModel(self, download):
        #remove failed from experiments and extrapolations
        # for exp in ('experiments', 'extrapolations'):
        #     for i in range(len(self.performance_model[exp])):
        #         if 'Success' in self.performance_model[exp][i] and not self.performance_model[exp][i]['Success']:
        #             self.performance_model['failed'].append(self.performance_model[exp][i])
        #             del self.performance_model[exp][i]
        if self.state == self.S_RUNNING:
            filter_extrapol = filter(lambda x: x['Success'], self.performance_model['extrapolations'])
            filter_exp = filter(lambda x: x['Success'], self.performance_model['experiments'])
            if len(filter_extrapol) > 0:
                self.performance_model['pareto'] = self.enforcer.get_aggregated_pareto({'experiments': filter_exp, 'extrapolations':filter_extrapol  })
        return self.performance_model



    def add_experiment(self, experiment, isProfile):
        exp_set = 'experiments'
        if not isProfile:
            exp_set = 'extrapolations'
        
        self.performance_model[exp_set].append(experiment)
        # if experiment['ImplementationID'] not in self.performance_model[exp_set]:
        #     self.performance_model[exp_set][str(experiment['ImplementationID'])] = []
        # self.performance_model[exp_set][str(experiment['ImplementationID'])].append(experiment)

  
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