import logging

from functools import wraps

logging_level = logging.DEBUG

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(lineno)d %(message)s')

'''Where to put logs (directory).
'''
log_dir_path = None

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging_level)

def set_logging_level(level):
    logging_level = level
    stream_handler.setLevel(level)

def register_logger(logger):
    logger.addHandler(stream_handler)

def create_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)
    register_logger(logger)
    hdlr = logging.FileHandler('/tmp/conpaassql-contrail.log')
    
    logger.addHandler(hdlr)
    return logger

def create_func_log(logger):
    def func_log(func):
        func_name = '%s.%s' % (func.__module__, func.__name__)
        
        @wraps(func)
        def decorated(*args, **kwargs):
            logger.debug('Entering function %s' % func_name)
            
            try:
                return func(*args, **kwargs)
            finally:
                logger.debug('Leaving function %s' % func_name)
        
        return decorated
    
    return func_log

def create_method_log(logger):
    def method_log(func):
        @wraps(func)
        def decorated(self, *args, **kwargs):
            method_name = '%s.%s.%s' % (self.__class__.__module__,
                                self.__class__.__name__, func.__name__)
            
            logger.debug('Entering method %s' % method_name)
            
            try:
                return func(self, *args, **kwargs)
            finally:
                logger.debug('Leaving method %s' % method_name)
        
        return decorated
    
    return method_log

def get_logger(name):
    #return logging.getLogger(name)
    return create_logger(name)

def get_logger_plus(name):
    logger = get_logger(name)    
    return logger, create_func_log(logger), create_method_log(logger)
