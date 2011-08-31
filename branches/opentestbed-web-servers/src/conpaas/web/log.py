'''
Created on Feb 9, 2011

@author: ielhelw
'''

import logging

logging_level = logging.DEBUG
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
_inited = False

def _register_logger(logger):
  for h in handlers:
    logger.addHandler(h)

def create_logger(name):
  logger = logging.getLogger(name)
  logger.setLevel(logging_level)
  if not _inited: return logger
  _register_logger(logger)
  loggers.append(logger)
  return logger

def init(log_file):
  global _inited
  if _inited: return
  _inited = True
  global handlers, loggers
  handlers = []
  loggers = []
  file_handler = logging.FileHandler(log_file)
  file_handler.setFormatter(log_formatter)
  handlers.append(file_handler)
  
#  import sys
#  err_handler = logging.StreamHandler(sys.stderr)
#  err_handler.setFormatter(log_formatter)
#  handlers.append(err_handler)

