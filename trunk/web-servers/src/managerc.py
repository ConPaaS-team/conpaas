#!/usr/bin/python
'''
Created on Mar 29, 2011

@author: ielhelw
'''

from optparse import OptionParser
import sys, time

from conpaas.web.manager import client
from inspect import isfunction, currentframe
from pprint import pprint

def getState(args):
  '''Get the state of a deployment'''
  parser = OptionParser(usage='getState')
  options, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.getState(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response
    else:
      print response['state']

def getStateChanges(args):
  '''Get the state change history of a deployment'''
  parser = OptionParser(usage='getStateChanges')
  options, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.getStateChanges(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response
    else:
      for state in response['state_log']:
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(state['time'])), state['state'], state['reason']

def startup(args):
  '''Startup a deployment'''
  parser = OptionParser(usage='startup')
  options, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.startup(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response
    else:
      print response['state']

def shutdown(args):
  '''Shutdown a deployment'''
  parser = OptionParser(usage='shutdown')
  options, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.shutdown(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response
    else:
      print response['state']

def add(args):
  '''Add more service nodes to a deployment'''
  parser = OptionParser(usage='add')
  parser.add_option('-l', '--proxy', dest='proxy', type='int', default=0)
  parser.add_option('-w', '--web', dest='web', type='int', default=0)
  parser.add_option('-p', '--php', dest='php', type='int', default=0)
  opts, pargs = parser.parse_args(args)
  if pargs\
  or (opts.proxy == 0 and opts.web == 0 and opts.php == 0)\
  or opts.proxy < 0 or opts.web < 0 or opts.php < 0:
    parser.print_help()
  else:
    response = client.addServiceNodes(host, port, proxy=opts.proxy, web=opts.web, php=opts.php)
    if 'opState' not in response or response['opState'] != 'OK':
      print response

def remove(args):
  '''Remove some service nodes from a deployment'''
  parser = OptionParser(usage='remove')
  parser.add_option('-l', '--proxy', dest='proxy', type='int', default=0)
  parser.add_option('-w', '--web', dest='web', type='int', default=0)
  parser.add_option('-p', '--php', dest='php', type='int', default=0)
  opts, pargs = parser.parse_args(args)
  if pargs\
  or (opts.proxy == 0 and opts.web == 0 and opts.php == 0)\
  or opts.proxy < 0 or opts.web < 0 or opts.php < 0:
    parser.print_help()
  else:
    response = client.removeServiceNodes(host, port, proxy=opts.proxy, web=opts.web, php=opts.php)
    if 'opState' not in response or response['opState'] != 'OK':
      print response

def listServiceNodes(args):
  '''Get a list of service nodes'''
  parser = OptionParser(usage='listServiceNodes')
  opts, pargs = parser.parse_args(args)
  if len(pargs) != 0:
    parser.print_help()
  else:
    response = client.listServiceNodes(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response
    else:
      all = list(set(response['proxy'] + response['web'] + response['php']))
      for i in all:
        print i,
        if i in response['proxy']: print 'PROXY',
        if i in response['web']: print 'WEB',
        if i in response['php']: print 'PHP',
        print

def getServiceNode(args):
  '''Get information about a single service node'''
  parser = OptionParser(usage='getServiceNode <nodeId>')
  opts, pargs = parser.parse_args(args)
  if len(pargs) != 1:
    parser.print_help()
  else:
    response = client.getServiceNodeById(host, port, args[0])
    if 'opState' not in response or response['opState'] != 'OK':
      print response
    else:
      print response['serviceNode']['id'], response['serviceNode']['ip'],
      if  response['serviceNode']['isRunningProxy']: print 'PROXY',
      if  response['serviceNode']['isRunningWeb']: print 'WEB',
      if  response['serviceNode']['isRunningPHP']: print 'PHP',
      print

def listCodeVersions(args):
  '''List identifiers of all code versions stored by a deployment'''
  parser = OptionParser(usage='listCodeVersions')
  opts, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.listCodeVersions(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response
    else:
      for c in response['codeVersions']:
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(c['time'])),
        print c['codeVersionId'],
        if 'current' in c and c['current']: print 'CURRENT',
        print c['filename'], c['description']

def downloadCodeVersion(args):
  '''Get a URL to the code version'''
  parser = OptionParser(usage='downloadCodeVersion <codeVersionId>')
  opts, pargs = parser.parse_args(args)
  if len(pargs) != 1:
    parser.print_help()
  else:
    response = client.downloadCodeVersion(host, port, args[0])
    print response

def uploadCodeVersion(args):
  '''Upload a new code version'''
  parser = OptionParser(usage='uploadCodeVersion <filename>')
  opts, pargs = parser.parse_args(args)
  if len(pargs) != 1:
    parser.print_help()
  else:
    response = client.uploadCodeVersion(host, port, args[0])
    if 'opState' not in response or response['opState'] != 'OK':
      print response
    else:
      print 'codeVersionId:', response['codeVersionId']

def getConfiguration(args):
  '''Get the configuration of a deployment'''
  parser = OptionParser(usage='getConfiguration')
  opts, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.getConfiguration(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response
    else:
      print 'Current codeVersions:', response['codeVersionId']
      print 'PHP configuration:'
      for i in response['phpconf']:
        print '  %s:' % i, response['phpconf'][i]

def updateConfiguration(args):
  '''Update the configuration of a deployment'''
  parser = OptionParser(usage='updateConfiguration')
  parser.add_option('-c', '--code', dest='codeVersionId', type='string', default=None)
  parser.add_option('-p', '--phpconfig', action='append', dest='phpconfig', type='string', default=[], help='Multiple "-p" options can be supplied each of the form "key=value"')
  opts, pargs = parser.parse_args(args)
  php = {}
  for config in opts.phpconfig:
    pair = config.split('=', 1)
    if len(pair) != 2:
      parser.print_help()
      sys.exit(1)
    php[pair[0]] = pair[1]
  if pargs or (not opts.phpconfig and opts.codeVersionId == None):
    parser.print_help()
  else:
    response = client.updateConfiguration(host, port, codeVersionId=opts.codeVersionId, phpconf=php)
    if 'opState' not in response or response['opState'] != 'OK':
      print response

def getHighLevelMonitoring(args):
  '''Get the average request rate and throughput'''
  parser = OptionParser(usage='getHighLevelMonitoring')
  opts, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.getHighLevelMonitoring(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response
    else:
      print 'Avg. Throughput:', response['avg_throughput']
      print 'Avg. Request rate:', response['avg_throughput']
      print 'Avg. Error rate:', response['avg_throughput']

def getLog(args):
  '''Get raw logging'''
  parser = OptionParser(usage='getLog')
  opts, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.getLog(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response
    else:
      print response['log']

def help(args=[]):
  '''Print the help menu'''
  l = ['add',
       'downloadCodeVersion',
       'getConfiguration',
       'getHighLevelMonitoring',
       'getLog',
       'getServiceNode',
       'getState',
       'getStateChanges',
       'help',
       'listCodeVersions',
       'listServiceNodes',
       'remove',
       'shutdown',
       'startup',
       'updateConfiguration',
       'uploadCodeVersion']
  l.sort()
  module = sys.modules[__name__]
  l = [ getattr(module, i) for i in l ]
  print 'Usage:', sys.argv[0], 'host port action [options]'
  print
  print 'Action could be one of:'
  print ' %-25s   %s' % ('[ACTION]', '[DESCRIPTION]')
  for func in l:
    print ' %-25s   %s' % (func.__name__, func.__doc__)

if __name__ == '__main__':
  if len(sys.argv) < 4:
    help()
    sys.exit(1)
  global host, port
  host, port = sys.argv[1:3]
  if hasattr(sys.modules[__name__], sys.argv[3]):
    func = getattr(sys.modules[__name__], sys.argv[3])
    if not isfunction(func):
      help()
      sys.exit(1)
    func(sys.argv[4:])
  else:
    help()
    sys.exit(1)
    