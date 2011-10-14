'''
Copyright (C) 2010-2011 Contrail consortium.

This file is part of ConPaaS, an integrated runtime environment 
for elastic cloud applications.

ConPaaS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ConPaaS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.


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

