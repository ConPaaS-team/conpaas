#!/usr/bin/python
'''
Copyright (c) 2010-2012, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of 
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the Contrail consortium nor the
    names of its contributors may be used to endorse
    or promote products derived from this software 
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.


Created on Feb 15, 2012

@author: schuett
'''

from optparse import OptionParser
import sys, time, urlparse
from inspect import isfunction
from os import environ

try:
  from conpaas.core import https
  from conpaas.services.scalaris.manager import client
except ImportError as e:
  print >>sys.stderr, 'Failed to locate conpaas modules'
  print >>sys.stderr, e
  sys.exit(1)

def get_service_info(args):
  '''Get the state of a deployment'''
  parser = OptionParser(usage='get_service_info')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.get_service_info(host, port)
    print 'service type:', response['type']
    print 'state:', response['state']

def startup(args):
  '''Startup a deployment'''
  parser = OptionParser(usage='startup')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.startup(host, port)
    print response['state']

def add_nodes(args):
  '''Add more service nodes to a deployment'''
  parser = OptionParser(usage='add_nodes')
  parser.add_option('-c', '--count', dest='count', type='int', default=0)
  opts, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.add_nodes(host, port, count=opts.count)

def remove_nodes(args):
  '''Remove some service nodes from a deployment'''
  parser = OptionParser(usage='remove_nodes')
  parser.add_option('-c', '--count', dest='count', type='int', default=0)
  opts, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.remove_nodes(host, port, count=opts.count)

def list_nodes(args):
  '''Get a list of service nodes'''
  parser = OptionParser(usage='list_nodes')
  _, pargs = parser.parse_args(args)
  if len(pargs) != 0:
    parser.print_help()
  else:
    response = client.list_nodes(host, port)
    all = list(set(response['scalaris']))
    for i in all:
      print i

def help(args=[]):
  '''Print the help menu'''
  l = ['add_nodes',
       'get_service_info',
       'help',
       'list_nodes',
       'remove_nodes',
       'startup']
  l.sort()
  module = sys.modules[__name__]
  l = [ getattr(module, i) for i in l ]
  print 'Usage:', sys.argv[0], 'URL ACTION [options]'
  print
  print 'Action could be one of:'
  print ' %-25s   %s' % ('[ACTION]', '[DESCRIPTION]')
  for func in l:
    print ' %-25s   %s' % (func.__name__, func.__doc__)

if __name__ == '__main__':
  if len(sys.argv) < 3:
    help()
    sys.exit(1)
  
  try:  
    certs_dir = environ['CONPAAS_CERTS_DIR']
  except KeyError: 
    print "Please set the environment variable CONPAAS_CERTS_DIR"
    sys.exit(1)

  try:
      https.client.conpaas_init_ssl_ctx(certs_dir, 'user')
  except Exception as e:
      print e

  global host, port
  try:
    url = urlparse.urlparse(sys.argv[1], scheme='http')
    host = url.hostname
    port = url.port or 443
    if not host: raise Exception()
  except:
    print >>sys.stderr, 'Invalid URL'
    sys.exit(1)
  
  if hasattr(sys.modules[__name__], sys.argv[2]):
    func = getattr(sys.modules[__name__], sys.argv[2])
    if not isfunction(func):
      help()
      sys.exit(1)
    try:
      func(sys.argv[3:])
    except Exception as e:
      print >>sys.stderr, e
  else:
    help()
    sys.exit(1)
    
