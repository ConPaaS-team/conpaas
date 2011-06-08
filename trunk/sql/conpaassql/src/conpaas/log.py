'''
Created on Feb 9, 2011

@author: ielhelw
'''

import logging

logging_level = logging.DEBUG

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(lineno)d %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging_level)
 
#file_handler = logging.FileHandler(filename, mode, encoding, delay)
#file_handler.setFormatter(log_formatter)

def set_logging_level(level):
    logging_level = level
    stream_handler.setLevel(level)

def register_logger(logger):
    logger.addHandler(stream_handler)
#  logger.addHandler(file_handler)

def create_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)
    register_logger(logger)
    hdlr = logging.FileHandler('/tmp/contrail.log')
    logger.addHandler(hdlr)
    return logger