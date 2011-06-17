#!/usr/bin/python
'''
Created on Mar 29, 2011

@author: ielhelw
'''

from optparse import OptionParser
import sys, time, urlparse

from conpaas.web.manager import client
from inspect import isfunction

def getState(args):
  '''Get the state of a deployment'''
  parser = OptionParser(usage='getState')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.getState(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response['error']
    else:
      print response['state']

def getStateChanges(args):
  '''Get the state change history of a deployment'''
  parser = OptionParser(usage='getStateChanges')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.getStateChanges(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response['error']
    else:
      if response['state_log']:
        for state in response['state_log']:
          print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(state['time'])), state['state'], state['reason']
      else:
        print 'No changes in history'

def startup(args):
  '''Startup a deployment'''
  parser = OptionParser(usage='startup')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.startup(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response['error']
    else:
      print response['state']

def shutdown(args):
  '''Shutdown a deployment'''
  parser = OptionParser(usage='shutdown')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.shutdown(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response['error']
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
      print response['error']

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
      print response['error']

def listServiceNodes(args):
  '''Get a list of service nodes'''
  parser = OptionParser(usage='listServiceNodes')
  _, pargs = parser.parse_args(args)
  if len(pargs) != 0:
    parser.print_help()
  else:
    response = client.listServiceNodes(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response['error']
    else:
      print '%-20s %s' % ('Service Node', 'Role(s)')
      all = list(set(response['proxy'] + response['web'] + response['php']))
      for i in all:
        print '%-20s%s' % (i,
                            (i in response['proxy'] and ' PROXY' or '')
                              + (i in response['web'] and ' WEB' or '')
                              + (i in response['php'] and ' PHP' or ''))

def getServiceNode(args):
  '''Get information about a single service node'''
  parser = OptionParser(usage='getServiceNode <nodeId>')
  _, pargs = parser.parse_args(args)
  if len(pargs) != 1:
    parser.print_help()
  else:
    response = client.getServiceNodeById(host, port, args[0])
    if 'opState' not in response or response['opState'] != 'OK':
      print response['error']
    else:
      print '%-20s %-20s %s' % ('Service Node', 'Address', 'Role(s)')
      print '%-20s %-20s' % (response['serviceNode']['id'], response['serviceNode']['ip']),
      if  response['serviceNode']['isRunningProxy']: print 'PROXY',
      if  response['serviceNode']['isRunningWeb']: print 'WEB',
      if  response['serviceNode']['isRunningPHP']: print 'PHP',
      print

def listCodeVersions(args):
  '''List identifiers of all code versions stored by a deployment'''
  parser = OptionParser(usage='listCodeVersions')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.listCodeVersions(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response['error']
    else:
      print '%-21s %-20s %-20s %-20s %s' % ('Upload Date', 'Identifier', 'Live', 'Name', 'Description')
      for c in response['codeVersions']:
        print '%-21s %-20s %-20s %-20s %s' % (
          time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(c['time'])),
          c['codeVersionId'],
          ('current' in c and c['current'] and 'YES') or '-',
          c['filename'],
          c['description'])

def downloadCodeVersion(args):
  '''Download a code version'''
  parser = OptionParser(usage='downloadCodeVersion <codeVersionId>')
  _, pargs = parser.parse_args(args)
  if len(pargs) != 1:
    parser.print_help()
  else:
    response = client.downloadCodeVersion(host, port, args[0])
    print response

def uploadCodeVersion(args):
  '''Upload a new code version'''
  parser = OptionParser(usage='uploadCodeVersion <filename>')
  _, pargs = parser.parse_args(args)
  if len(pargs) != 1:
    parser.print_help()
  else:
    response = client.uploadCodeVersion(host, port, args[0])
    if 'opState' not in response or response['opState'] != 'OK':
      print response['error']
    else:
      print 'codeVersionId:', response['codeVersionId']

def getConfiguration(args):
  '''Get the configuration of a deployment'''
  parser = OptionParser(usage='getConfiguration')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.getConfiguration(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response['error']
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
      print response['error']

def getHighLevelMonitoring(args):
  '''Get the average request rate and throughput'''
  parser = OptionParser(usage='getHighLevelMonitoring')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.getHighLevelMonitoring(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response['error']
    else:
      print 'Avg. Throughput:', response['avg_throughput']
      print 'Avg. Request rate:', response['avg_throughput']
      print 'Avg. Error rate:', response['avg_throughput']

def getLog(args):
  '''Get raw logging'''
  parser = OptionParser(usage='getLog')
  _, pargs = parser.parse_args(args)
  if pargs:
    parser.print_help()
  else:
    response = client.getLog(host, port)
    if 'opState' not in response or response['opState'] != 'OK':
      print response['error']
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
  global host, port
  try:
    url = urlparse.urlparse(sys.argv[1], scheme='http')
    host = url.hostname
    port = url.port or 80
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
      print e
  else:
    help()
    sys.exit(1)
    