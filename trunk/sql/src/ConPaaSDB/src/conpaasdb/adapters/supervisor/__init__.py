import xmlrpclib
import inject

from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class SupervisorFaults:
    UNKNOWN_METHOD = 1
    INCORRECT_PARAMETERS = 2
    BAD_ARGUMENTS = 3
    SIGNATURE_UNSUPPORTED = 4
    SHUTDOWN_STATE = 6
    BAD_NAME = 10
    NO_FILE = 20
    NOT_EXECUTABLE = 21
    FAILED = 30
    ABNORMAL_TERMINATION = 40
    SPAWN_ERROR = 50
    ALREADY_STARTED = 60
    NOT_RUNNING = 70
    SUCCESS = 80
    ALREADY_ADDED = 90
    STILL_RUNNING = 91
    CANT_REREAD = 92

class SupervisorProcessStates:
    STOPPED = 0
    STARTING = 10
    RUNNING = 20
    BACKOFF = 30
    STOPPING = 40
    EXITED = 100
    FATAL = 200
    UNKNOWN = 1000

class SupervisorSettings(object):
    user = None
    password = None
    port = None

class Supervisor(object):
    settings = inject.attr(SupervisorSettings)
    
    @mlog
    def __init__(self):
        url = 'http://%(user)s:%(password)s@%(host)s:%(port)s/RPC2' % dict(
                user = self.settings.user,
                password = self.settings.password,
                host = '127.0.0.1',
                port = self.settings.port
            )
        
        self.rpc = xmlrpclib.Server(url)
    
    @mlog
    def start(self, name):
        return self.rpc.supervisor.startProcess(name)
    
    @mlog
    def stop(self, name):
        return self.rpc.supervisor.stopProcess(name)
    
    @mlog
    def info(self, name):
        return self.rpc.supervisor.getProcessInfo(name)
