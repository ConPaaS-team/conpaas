'''
Created on Feb 8, 2011

@author: ielhelw

- What is a deployment?
  A set of VMs logically grouped into 3 roles; web servers, php and load balancers.

- What is the configuration?
  web servers:    port, doc_root and list of php (ip, port)
  php:           port
  load balancer:  port, list of web servers (ip, port)
  CODE to be placed at doc_root of all webserver VMs. Any file ending with
  '.php' is considered a dynamic script and will be passed to an php process.
  CODE should be located at the same directory path at all web servers and
  phps.

- How is a deployment started?
  A VM is created by the cloud front-end to host the MANAGER. The manager reads
  the initial configuration (from cloud storage or service?) and starts
  requesting VMs as needed by the configuration. Each VM will host an AGENT
  that is responsible for starting processes in it. The MANAGER will assign
  roles to each VM by instructing their AGENTs to run certain processes.
  
'''

from threading import Thread
import tempfile, os, os.path, tarfile, time, stat

from conpaas.log import create_logger
from conpaas.web.agent import client
from conpaas.web.manager.config import ServiceNode, CodeVersion, Configuration
from conpaas.web.misc import archive_supported_name, archive_open,\
  archive_get_members, archive_close, archive_supported_extensions,\
  archive_get_type

logger = create_logger(__name__)

# memcache keys
CONFIG = 'config'
DEPLOYMENT_STATE = 'deployment_state'

S_INIT = 'INIT'
S_PROLOGUE = 'PROLOGUE'
S_RUNNING = 'RUNNING'
S_ADAPTING = 'ADAPTING'
S_EPILOGUE = 'EPILOGUE'
S_STOPPED = 'STOPPED'
S_ERROR = 'ERROR'

exposed_functions = {}

E_CONFIG_READ_FAILED = 0
E_CONFIG_COMMIT_FAILED = 1
E_ARGS_INVALID = 2
E_ARGS_UNEXPECTED = 3
E_ARGS_MISSING = 4
E_IAAS_REQUEST_FAILED = 5
E_STATE_ERROR = 6
E_CODE_VERSION_ERROR = 7
E_UNKNOWN = 8

E_STRINGS = [
  'Failed to read configuration',
  'Failed to commit configuration',
  'Invalid arguments',
  'Unexpected arguments %s', # 1 param (a list)
  'Missing argument "%s"', # 1 param
  'Failed to request resources from IAAS',
  'Cannot perform requested operation in current state',
  'No code version selected',
  'Unknown error',
]

def init(memcache_in, iaas_in, code_repo_in, logfile_in):
  global memcache, iaas, code_repo, logfile
  memcache, iaas, code_repo, logfile = memcache_in,\
                                       iaas_in, code_repo_in, logfile_in

state_log = []

def _state_get():
  return memcache.get(DEPLOYMENT_STATE)

def _state_set(target_state, msg=''):
  memcache.set(DEPLOYMENT_STATE, target_state)
  state_log.append({'time': time.time(), 'state': target_state, 'reason': msg})

def _configuration_get():
  return memcache.get(CONFIG)

def _configuration_set(config):
  memcache.set(CONFIG, config)

class ManagerException(Exception):
  def __init__(self, code, *args, **kwargs):
    self.code = code
    self.args = args
    if 'detail' in kwargs:
      self.message = '%s DETAIL:%s' % ( (E_STRINGS[code] % args), str(kwargs['detail']) )
    else:
      self.message = E_STRINGS[code] % args

def expose(http_method):
  def decorator(func):
    if http_method not in exposed_functions:
      exposed_functions[http_method] = {}
    exposed_functions[http_method][func.__name__] = func
    def wrapped(*args, **kwargs):
      return func(*args, **kwargs)
    return wrapped
  return decorator

def check_nofiles(kwargs, exceptfor=[]):
  for key in kwargs:
    if isinstance(kwargs[key], dict) and key not in exceptfor:
      raise ManagerException(E_ARGS_UNEXPECTED, [key], detail='Not expecting a file in "%s"' % key)

@expose('GET')
def getState(kwargs):
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  return {'opState': 'OK', 'state': _state_get()}

def wait_for_nodes(nodes, poll_interval=10):
  logger.debug('wait_for_nodes: going to start polling')
  done = []
  while len(nodes) > 0:
    for i in nodes:
      up = True
      try:
        if i['ip'] != '':
          client.getPHPState(i['ip'], 5555)
        else:
          up = False
      except client.AgentException: pass
      except: up = False
      if up:
        done.append(i)
    nodes = [ i for i in nodes if i not in done]
    if len(nodes):
      logger.debug('wait_for_nodes: waiting for %d nodes' % len(nodes))
      time.sleep(poll_interval)
      no_ip_nodes = [ i for i in nodes if i['ip'] == '' ]
      if no_ip_nodes:
        logger.debug('wait_for_nodes: refreshing %d nodes' % len(no_ip_nodes))
        refreshed_list = iaas.listVMs()
        for i in no_ip_nodes:
          i['ip'] = refreshed_list[i['id']]['ip']
  logger.debug('wait_for_nodes: All nodes are ready %s' % str(done))
  

@expose('POST')
def startup(kwargs):
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  config = _configuration_get()
#  nodes = memcache.get(NODES) # Get list of available vm IDs
  
  dstate = _state_get()
  if dstate != S_INIT and dstate != S_STOPPED:
    return {'opState': 'ERROR', 'error': ManagerException(E_STATE_ERROR).message}
  
  _state_set(S_PROLOGUE, msg='Starting up')
  Thread(target=do_startup, args=[config]).start()
  return {'opState': 'OK', 'state': S_PROLOGUE}

def do_startup(config):
  if config.web_count == 1 \
  and (config.proxy_count == 0 or config.php_count == 0):# at least one is packed
    if config.proxy_count == 0 and config.php_count == 0:# packed
      serviceNodeKwargs = [ {'runProxy':True, 'runWeb':True, 'runPHP':True} ]
    elif config.proxy_count == 0 and config.php_count > 0:# proxy packed, php separated
      serviceNodeKwargs = [ {'runProxy':True, 'runWeb':True},
                       {'runPHP':True} ]
    elif config.proxy_count > 0 and config.php_count == 0:# proxy separated, php packed
      serviceNodeKwargs = [ {'runProxy':True},
                       {'runWeb':True, 'runPHP':True} ]
  else:
    if config.proxy_count < 1: config.proxy_count = 1 # have to have at least one proxy
    if config.php_count < 1: config.php_count = 1 # have to have at least one php
    serviceNodeKwargs = [ {'runProxy':True} for i in range(config.proxy_count) ]
    serviceNodeKwargs.extend([ {'runWeb':True} for i in range(config.web_count) ])
    serviceNodeKwargs.extend([ {'runPHP':True} for i in range(config.php_count) ])
  
  logger.debug('do_startup: Going to request %d new nodes' % len(serviceNodeKwargs))
  node_instances = []
  try:
    for kwargs in serviceNodeKwargs:
      node_instances.append(iaas.newInstance())
  except:
    logger.critical('do_startup: Failed to request new nodes. Need %d, got %d only' % (len(serviceNodeKwargs), len(node_instances)))
    logger.critical('do_startup: Going to release %d nodes' % (len(node_instances)))
    for node in node_instances:
      try:
        iaas.killInstance(node['id'])
      except:
        logger.critical('do_startup: Failed to kill node %s', node['id'])
    _state_set(S_ERROR, msg='Failed to request new nodes')
    return
  
#  update mappings after waiting for all nodes (wait for IPs)
  wait_for_nodes(node_instances)
  config.serviceNodes.clear()
  i = 0
  for kwargs in serviceNodeKwargs:
    config.serviceNodes[node_instances[i]['id']] = ServiceNode(node_instances[i]['id'], **kwargs)
    i += 1
  config.update_mappings()
  
  # stage the code files
  if config.currentCodeVersion != None:
    for serviceNode in config.serviceNodes.values():
      try:
        client.updateCode(serviceNode.ip, 5555, config.currentCodeVersion, config.codeVersions[config.currentCodeVersion].type, os.path.join(code_repo, config.currentCodeVersion))
      except client.AgentException as e:
        logger.exception('Failed to update code at node %s' % str(serviceNode))
        _state_set(S_ERROR, msg='Failed to update code at node %s' % str(serviceNode))
        return
  
  # issue orders to agents to start PHP inside
  for serviceNode in config.getPHPServiceNodes():
    try:
      client.createPHP(serviceNode.ip, 5555, config.php_config.port, config.php_config.scalaris, config.php_config.php_conf.conf)
    except client.AgentException as e:
        logger.exception('Failed to start php at node %s' % str(serviceNode))
        _state_set(S_ERROR, msg='Failed to start php at node %s' % str(serviceNode))
        return
    
  
  # issue orders to agents to start web servers inside
  for serviceNode in config.getWebServiceNodes():
    try:
      client.createWebServer(serviceNode.ip, 5555, config.web_config.doc_root, config.web_config.port, config.web_config.php_backends)
    except client.AgentException as e:
        logger.exception('Failed to start web at node %s' % str(serviceNode))
        _state_set(S_ERROR, msg='Failed to start web at node %s' % str(serviceNode))
        return
  
  # issue orders to agents to start proxy inside
  for serviceNode in config.getProxyServiceNodes():
    try:
      if config.currentCodeVersion != None:
        client.createHttpProxy(serviceNode.ip, 5555, config.proxy_config.port, config.proxy_config.web_backends, config.currentCodeVersion)
      else:
        client.createHttpProxy(serviceNode.ip, 5555, config.proxy_config.port, config.proxy_config.web_backends, '')
    except client.AgentException as e:
        logger.exception('Failed to start proxy at node %s' % str(serviceNode))
        _state_set(S_ERROR, msg='Failed to start proxy at node %s' % str(serviceNode))
        return
  
  _configuration_set(config) # update configuration
  _state_set(S_RUNNING)

@expose('POST')
def shutdown(kwargs):
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  
  dstate = _state_get()
  if dstate != S_RUNNING:
    return {'opState': 'ERROR', 'error': ManagerException(E_STATE_ERROR).message}
  
  config = _configuration_get()
  _state_set(S_EPILOGUE, msg='Shutting down')
  Thread(target=do_shutdown, args=[config]).start()
  return {'opState': 'OK', 'state': S_EPILOGUE}

def do_shutdown(config):
  for serviceNode in config.getProxyServiceNodes():
    try: client.stopHttpProxy(serviceNode.ip, 5555)
    except client.AgentException as e:
        logger.exception('Failed to stop proxy at node %s' % str(serviceNode))
        _state_set(S_ERROR, msg='Failed to stop proxy at node %s' % str(serviceNode))
        return
    
  for serviceNode in config.getWebServiceNodes():
    try: client.stopWebServer(serviceNode.ip, 5555)
    except client.AgentException as e:
        logger.exception('Failed to stop web at node %s' % str(serviceNode))
        _state_set(S_ERROR, msg='Failed to stop web at node %s' % str(serviceNode))
        return
  
  for serviceNode in config.getPHPServiceNodes():
    try: client.stopPHP(serviceNode.ip, 5555)
    except client.AgentException as e:
        logger.exception('Failed to stop php at node %s' % str(serviceNode))
        _state_set(S_ERROR, msg='Failed to stop php at node %s' % str(serviceNode))
        return
  
  for serviceNode in config.serviceNodes.values():
    iaas.killInstance(serviceNode.vmid)
  
  config.serviceNodes = {}
  
  _state_set(S_STOPPED)
  _configuration_set(config)

@expose('POST')
def addServiceNodes(kwargs):
  try: check_nofiles(kwargs)
  except ManagerException as e: return {'opState': 'ERROR', 'error': e.message}
  
  config = _configuration_get()
  dstate = _state_get()
  if dstate != S_RUNNING:
    return {'opState': 'ERROR', 'error': ManagerException(E_STATE_ERROR).message}
  
  php = 0
  web = 0
  proxy = 0
  if 'php' in kwargs:
    if not kwargs['php'].isdigit():
      return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected an integer value for "php"').message}
    php = int(kwargs.pop('php'))
    if php < 0: return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected a positive integer value for "php"').message}
  if 'web' in kwargs:
    if not kwargs['web'].isdigit():
      return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected an integer value for "web"').message}
    web = int(kwargs.pop('web'))
    if web < 0: return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected a positive integer value for "web"').message}
  if 'proxy' in kwargs:
    if not kwargs['proxy'].isdigit():
      return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected an integer value for "proxy"').message}
    proxy = int(kwargs.pop('proxy'))
    if proxy < 0: return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected a positive integer value for "proxy"').message}
  if (php + web + proxy) < 1:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_MISSING, ['php', 'web', 'proxy'], detail='Need a positive value for at least one').message}
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  
  _state_set(S_ADAPTING, msg='Going to add proxy=%d, web=%d, php=%d' % (proxy, web, php))
  Thread(target=do_addServiceNodes, args=[config, proxy, web, php]).start()
  ret = {'opState': 'OK'}
  return ret

def do_addServiceNodes(config, proxy, web, php):
  webNodesNew = []
  proxyNodesNew = []
  phpNodesNew = []
  
  webNodesKill = []
  phpNodesKill = []
  
  proxyPacked = config.proxy_count == 0
  phpPacked = config.php_count == 0
  
  if config.web_count == 1:
    if web > 0:
      if config.proxy_count == 0 and config.php_count == 0: # both are packed
        # create web count + 1 because old web server will be removed
        webNodesNew += [ {'runWeb':True} for i in range(web + 1) ]
        # remove old web server
        webNodesKill.append(config.getWebServiceNodes()[0])
        # in the process we created an extra proxy
        proxy -= 1
        proxyPacked = False
        # in the process we created an extra PHP and need to remove the old one
        phpNodesNew += [ {'runPHP':True} ]
        php -= 1
        phpNodesKill.append(config.getPHPServiceNodes()[0])
        phpPacked = False
      elif config.proxy_count == 0: # proxy only us packed
        # create web count + 1 because old web server will be removed
        webNodesNew += [ {'runWeb':True} for i in range(web + 1) ]
        # remove old web server
        webNodesKill.append(config.getWebServiceNodes()[0])
        # in the process we created an extra proxy
        proxy -= 1
        proxyPacked = False
      elif config.php_count == 0: # PHP only is packed
        # create web count
        webNodesNew += [ {'runWeb':True} for i in range(web) ]
        # in the process we created an extra PHP and need to remove the old one
        phpNodesNew += [ {'runPHP':True} ]
        php -= 1
        phpNodesKill.append(config.getPHPServiceNodes()[0])
        phpPacked = False
      else:
        webNodesNew += [ {'runWeb':True} for i in range(web) ]
    if php > 0:
      if phpPacked:
        phpNodesKill.append(config.getPHPServiceNodes()[0])
        phpPacked = False
      phpNodesNew += [ {'runPHP':True} for i in range(php) ]
    if proxy > 0:
      if proxyPacked:
        tmpWebNode = {'runWeb':True, 'runPHP':phpPacked}
        if phpPacked:
          phpNodesKill.append(config.getWebServiceNodes()[0])
        webNodesKill.append(config.getWebServiceNodes()[0])
        webNodesNew.append(tmpWebNode)
        proxy -= 1
        proxyPacked = False
      proxyNodesNew += [ {'runProxy':True} for i in range(proxy) ]
  else:
    for i in range(php): phpNodesNew.append({'runPHP':True})
    for i in range(web): webNodesNew.append({'runWeb':True})
    for i in range(proxy): proxyNodesNew.append({'runProxy':True})
  
  for i in webNodesKill: i.isRunningWeb = False
  for i in phpNodesKill: i.isRunningPHP = False
  
  newNodes = []
  node_instances = []
  try:
    for i in proxyNodesNew + webNodesNew + phpNodesNew:
      node_instances.append(iaas.newInstance())
  except:
    logger.critical('do_addServiceNodes: Failed to request new nodes. Need %d, got %d only' % (len(proxyNodesNew + webNodesNew + phpNodesNew), len(node_instances)))
    # FIXME: What is the policy for failing to create new instances
    logger.critical('do_addServiceNodes: Going to release %d nodes' % (len(node_instances)))
    for node in node_instances:
      try:
        iaas.killInstance(node['id'])
      except:
        logger.critical('do_addServiceNodes: Failed to kill node %s', node['id'])
    _state_set(S_RUNNING, msg='Failed to request new nodes. Going to old configuration')
    return
  
  # update mappings after waiting for all nodes (wait for IPs)
  wait_for_nodes(node_instances)
  i = 0
  for kwargs in proxyNodesNew + webNodesNew + phpNodesNew:
    config.serviceNodes[node_instances[i]['id']] = ServiceNode(node_instances[i]['id'], **kwargs)
    newNodes += [ config.serviceNodes[node_instances[i]['id']] ]
    i += 1
  config.update_mappings()
  
  # stage code files in all new VMs
  if config.currentCodeVersion != None:
    for node in newNodes:
      if node not in config.serviceNodes:
        try: client.updateCode(node.ip, 5555, config.currentCodeVersion, config.codeVersions[config.currentCodeVersion].type, os.path.join(code_repo, config.currentCodeVersion))
        except client.AgentException as e:
          logger.exception('Failed to update code at node %s' % str(node))
          _state_set(S_ERROR, msg='Failed to update code at node %s' % str(node))
          return
  
  # create new service nodes
  for phpNode in [ node for node in newNodes if node.isRunningPHP ]:
    try: client.createPHP(phpNode.ip, 5555, config.php_config.port, config.php_config.scalaris, config.php_config.php_conf.conf)
    except client.AgentException as e:
        logger.exception('Failed to start php at node %s' % str(phpNode))
        _state_set(S_ERROR, msg='Failed to start php at node %s' % str(phpNode))
        return
  for webNode in [ node for node in newNodes if node.isRunningWeb ]:
    try: client.createWebServer(webNode.ip, 5555, config.web_config.doc_root, config.web_config.port, config.web_config.php_backends)
    except client.AgentException as e:
        logger.exception('Failed to start web at node %s' % str(webNode))
        _state_set(S_ERROR, msg='Failed to start web at node %s' % str(webNode))
        return
  for proxyNode in [ node for node in newNodes if node.isRunningProxy ]:
    try:
      if config.currentCodeVersion != None:
        client.createHttpProxy(proxyNode.ip, 5555, config.proxy_config.port, config.proxy_config.web_backends, config.currentCodeVersion)
      else:
        client.createHttpProxy(proxyNode.ip, 5555, config.proxy_config.port, config.proxy_config.web_backends, '')
    except client.AgentException as e:
      logger.exception('Failed to start proxy at node %s' % str(proxyNode))
      _state_set(S_ERROR, msg='Failed to start proxy at node %s' % str(proxyNode))
      return
  
  # update services
  if phpNodesNew:
    for webNode in [ i for i in config.serviceNodes.values() if i.isRunningWeb and i not in newNodes ]:
      try: client.updateWebServer(webNode.ip, 5555, config.web_config.doc_root, config.web_config.port, config.web_config.php_backends)
      except client.AgentException as e:
        logger.exception('Failed to update web at node %s' % str(webNode))
        _state_set(S_ERROR, msg='Failed to update web at node %s' % str(webNode))
        return
  if webNodesNew:
    for proxyNode in [ i for i in config.serviceNodes.values() if i.isRunningProxy and i not in newNodes ]:
      try:
        if config.currentCodeVersion != None:
          client.updateHttpProxy(proxyNode.ip, 5555, config.proxy_config.port, config.proxy_config.web_backends, config.currentCodeVersion)
        else:
          client.updateHttpProxy(proxyNode.ip, 5555, config.proxy_config.port, config.proxy_config.web_backends, '')
      except client.AgentException as e:
        logger.exception('Failed to update proxy at node %s' % str(proxyNode))
        _state_set(S_ERROR, msg='Failed to update proxy at node %s' % str(proxyNode))
        return
  
  # remove old ones
  for phpNode in phpNodesKill:
    try: client.stopPHP(phpNode.ip, 5555)
    except client.AgentException as e:
      logger.exception('Failed to stop php at node %s' % str(phpNode))
      _state_set(S_ERROR, msg='Failed to stop php at node %s' % str(phpNode))
      return
  for webNode in webNodesKill:
    try: client.stopWebServer(webNode.ip, 5555)
    except client.AgentException as e:
      logger.exception('Failed to stop web at node %s' % str(webNode))
      _state_set(S_ERROR, msg='Failed to stop web at node %s' % str(webNode))
      return
  
  config.web_count = len(config.getWebServiceNodes())
  config.php_count = len(config.getPHPServiceNodes())
  if config.php_count == 1 and config.getPHPServiceNodes()[0] in config.getWebServiceNodes():
    config.php_count = 0
  config.proxy_count = len(config.getProxyServiceNodes())
  if config.proxy_count == 1 and config.getProxyServiceNodes()[0] in config.getWebServiceNodes():
    config.proxy_count = 0
  
  _state_set(S_RUNNING)
  _configuration_set(config)

@expose('POST')
def removeServiceNodes(kwargs):
  try: check_nofiles(kwargs)
  except ManagerException as e: return {'opState': 'ERROR', 'error': e.message}
  
  config = _configuration_get()
  php = 0
  web = 0
  proxy = 0
  
  if 'php' in kwargs:
    if not kwargs['php'].isdigit():
      return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected an integer value for "php"').message}
    php = int(kwargs.pop('php'))
    if php < 0: return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected a positive integer value for "php"').message}
  if 'web' in kwargs:
    if not kwargs['web'].isdigit():
      return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected an integer value for "web"').message}
    web = int(kwargs.pop('web'))
    if web < 0: return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected a positive integer value for "web"').message}
  if 'proxy' in kwargs:
    if not kwargs['proxy'].isdigit():
      return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected an integer value for "proxy"').message}
    proxy = int(kwargs.pop('proxy'))
    if proxy < 0: return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Expected a positive integer value for "proxy"').message}
  if (php + web + proxy) < 1:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_MISSING, ['php', 'web', 'proxy'], detail='Need a positive value for at least one').message}
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  
  if config.web_count - web < 1: return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Not enough web nodes  will be left').message}
  
  if config.proxy_count - proxy < 1 and config.web_count - web > 1:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Not enough proxy nodes will be left').message}
  if config.proxy_count - proxy < 0: return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Cannot remove that many proxy nodes').message}
  
  if config.php_count - php < 1 and config.web_count - web > 1:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Not enough php nodes will be left').message}
  if config.php_count - php < 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Cannot remove that many php nodes').message}
  
  dstate = _state_get()
  if dstate != S_RUNNING:
    return {'opState': 'ERROR', 'error': ManagerException(E_STATE_ERROR).message}
  
  _state_set(S_ADAPTING, msg='Going to remove proxy=%d, web=%d, php=%d' %(proxy, web, php))
  Thread(target=do_removeServiceNodes, args=[config, proxy, web, php]).start()
  return {'opState': 'OK'}

def do_removeServiceNodes(config, proxy, web, php):
  phpNodesNew = []
  phpNodesKill = []
  webNodesNew = []
  webNodesKill = []
  proxyNodesKill = []
  
  if config.web_count - web == 1: # Need to look into packing options
    if web > 0:
      webNodesKill += config.getWebServiceNodes()[0:web]
    if php > 0:
      phpNodesKill += config.getPHPServiceNodes()[0:php] # kill all php
    if proxy > 0:
      if config.proxy_count - proxy == 0: # proxy needs to be packed
        webNodesKill += [config.getWebServiceNodes()[-1]] # kill the web server
        proxyNodesKill += config.getProxyServiceNodes()[0:proxy - 1] # kill all proxies except for 1
        webNodesNew += [config.getProxyServiceNodes()[-1]] # pack web server with the remaining proxy
      else: # no packing, simple
        proxyNodesKill += config.getProxyServiceNodes()[0:proxy]
    if config.php_count - php == 0: # need to pack a new on with the remaining web server
      if webNodesNew: tmpWebNode = webNodesNew[0]
      else: tmpWebNode = config.getWebServiceNodes()[-1]
      phpNodesNew = [tmpWebNode]
      if len(phpNodesKill) != len(config.getPHPServiceNodes()):
        phpNodesKill += config.getPHPServiceNodes()
  else:
    phpNodesKill += config.getPHPServiceNodes()[0:php]
    webNodesKill += config.getWebServiceNodes()[0:web]
    proxyNodesKill += config.getProxyServiceNodes()[0:proxy]
  
  
  for i in webNodesNew: i.isRunningWeb = True
  for i in webNodesKill: i.isRunningWeb = False
  for i in phpNodesNew: i.isRunningPHP = True
  for i in phpNodesKill: i.isRunningPHP = False
  for i in proxyNodesKill: i.isRunningProxy = False
  
  config.update_mappings()
  
  # new nodes
  for webNode in webNodesNew:
    try: client.createWebServer(webNode.ip, 5555, config.web_config.doc_root, config.web_config.port, config.web_config.php_backends)
    except client.AgentException as e:
      logger.exception('Failed to start web at node %s' % str(webNode))
      _state_set(S_ERROR, msg='Failed to start web at node %s' % str(webNode))
      return
  for phpNode in phpNodesNew:
    try: client.createPHP(phpNode.ip, 5555, config.php_config.port, config.php_config.scalaris, config.php_config.php_conf.conf)
    except client.AgentException as e:
      logger.exception('Failed to start php at node %s' % str(phpNode))
      _state_set(S_ERROR, msg='Failed to start php at node %s' % str(phpNode))
      return
  
  if phpNodesKill:
    for webNode in [ i for i in config.serviceNodes.values() if i.isRunningWeb and i not in webNodesKill ]:
      try: client.updateWebServer(webNode.ip, 5555, config.web_config.doc_root, config.web_config.port, config.web_config.php_backends)
      except client.AgentException as e:
        logger.exception('Failed to update web at node %s' % str(webNode))
        _state_set(S_ERROR, msg='Failed to update web at node %s' % str(webNode))
        return
  if webNodesKill:
    for proxyNode in [ i for i in config.serviceNodes.values() if i.isRunningProxy and i not in proxyNodesKill ]:
      try:
        if config.currentCodeVersion != None:
          client.updateHttpProxy(proxyNode.ip, 5555, config.proxy_config.port, config.proxy_config.web_backends, config.currentCodeVersion)
        else:
          client.updateHttpProxy(proxyNode.ip, 5555, config.proxy_config.port, config.proxy_config.web_backends, '')
      except client.AgentException as e:
        logger.exception('Failed to update proxy at node %s' % str(proxyNode))
        _state_set(S_ERROR, msg='Failed to update proxy at node %s' % str(proxyNode))
        return
  
  # remove nodes
  for phpNode in phpNodesKill:
    try: client.stopPHP(phpNode.ip, 5555)
    except client.AgentException as e:
      logger.exception('Failed to stop php at node %s' % str(phpNode))
      _state_set(S_ERROR, msg='Failed to stop php at node %s' % str(phpNode))
      return
  for webNode in webNodesKill:
    try: client.stopWebServer(webNode.ip, 5555)
    except client.AgentException as e:
      logger.exception('Failed to stop web at node %s' % str(webNode))
      _state_set(S_ERROR, msg='Failed to stop web at node %s' % str(webNode))
      return
  for proxyNode in proxyNodesKill:
    try: client.stopHttpProxy(proxyNode.ip, 5555)
    except client.AgentException as e:
      logger.exception('Failed to stop proxy at node %s' % str(proxyNode))
      _state_set(S_ERROR, msg='Failed to stop proxy at node %s' % str(proxyNode))
      return  
  
  for i in config.serviceNodes.values():
    if not i.isRunningPHP and not i.isRunningWeb and not i.isRunningProxy:
      del config.serviceNodes[i.vmid]
      iaas.killInstance(i.vmid)
  
  config.web_count = len(config.getWebServiceNodes())
  config.php_count = len(config.getPHPServiceNodes())
  if config.php_count == 1 and config.getPHPServiceNodes()[0] in config.getWebServiceNodes():
    config.php_count = 0
  config.proxy_count = len(config.getProxyServiceNodes())
  if config.proxy_count == 1 and config.getProxyServiceNodes()[0] in config.getWebServiceNodes():
    config.proxy_count = 0
  
  _state_set(S_RUNNING)
  _configuration_set(config)

@expose('GET')
def listServiceNodes(kwargs):
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  
  dstate = _state_get()
  if dstate != S_RUNNING and dstate != S_ADAPTING:
    return {'opState': 'ERROR', 'error': ManagerException(E_STATE_ERROR).message}
  
  config = _configuration_get()
  return {
          'opState': 'OK',
          'proxy': [ serviceNode.vmid for serviceNode in config.getProxyServiceNodes() ],
          'web': [ serviceNode.vmid for serviceNode in config.getWebServiceNodes() ],
          'php': [ serviceNode.vmid for serviceNode in config.getPHPServiceNodes() ]
          }

@expose('GET')
def getServiceNodeById(kwargs):
  try: check_nofiles(kwargs)
  except ManagerException as e: return {'opState': 'ERROR', 'error': e.message}
  
  if 'serviceNodeId' not in kwargs: return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_MISSING, 'serviceNodeId').message}
  serviceNodeId = kwargs.pop('serviceNodeId')
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  
  config = _configuration_get()
  if serviceNodeId not in config.serviceNodes: return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Invalid "serviceNodeId"').message}
  serviceNode = config.serviceNodes[serviceNodeId]
  return {
          'opState': 'OK',
          'serviceNode': {
                          'id': serviceNode.vmid,
                          'ip': serviceNode.ip,
                          'isRunningProxy': serviceNode.isRunningProxy,
                          'isRunningWeb': serviceNode.isRunningWeb,
                          'isRunningPHP': serviceNode.isRunningPHP,
                          }
          }

@expose('GET')
def listCodeVersions(kwargs):
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  config = _configuration_get()
  versions = []
  for version in config.codeVersions.values():
    item = {'codeVersionId': version.id, 'filename': version.filename, 'description': version.description, 'time': version.timestamp}
    if version.id == config.currentCodeVersion: item['current'] = True
    versions.append(item)
  versions.sort(cmp=(lambda x, y: cmp(x['time'], y['time'])), reverse=True)
  return {'opState': 'OK', 'codeVersions': versions}

@expose('GET')
def downloadCodeVersion(kwargs):
  if 'codeVersionId' not in kwargs:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_MISSING, 'codeVersionId').message}
  if isinstance(kwargs['codeVersionId'], dict):
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='codeVersionId should be a string').message}
  codeVersion = kwargs.pop('codeVersionId')
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  
  config = _configuration_get()
  
  if codeVersion not in config.codeVersions:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Invalid codeVersionId').message}
  
  filename = os.path.abspath(os.path.join(code_repo, codeVersion))
  if not filename.startswith(code_repo + '/') or not os.path.exists(filename):
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Invalid codeVersionId').message}
  return {'opState': 'DOWNLOAD', 'file': filename, 'response_filename': config.codeVersions[codeVersion].filename}

@expose('POST')
def uploadCodeVersion(kwargs):
  if 'code' not in kwargs:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_MISSING, 'code').message}
  code = kwargs.pop('code')
  if 'description' in kwargs: description = kwargs.pop('description')
  else: description = ''
  
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  if not isinstance(code, dict):
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='codeVersionId should be a file').message}
  if not archive_supported_name(code['filename']):
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='supported file archives types ' + str(archive_supported_extensions())).message}
  
  config = _configuration_get()
  fd, name = tempfile.mkstemp(prefix='code-', dir=code_repo)
  fd = os.fdopen(fd, 'w')
  upload = code['file']
  codeVersionId = os.path.basename(name)
  
  bytes = upload.read(2048)
  while len(bytes) != 0:
    fd.write(bytes)
    bytes = upload.read(2048)
  fd.close()
  
  arch = archive_open(name)
  if arch == None:
    os.remove(name)
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Invalid archive format').message}
  
  for fname in archive_get_members(arch):
    if fname.startswith('/') or fname.startswith('..'):
      archive_close(arch)
      os.remove(name)
      return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Absolute file names are not allowed in archive members').message}
  archive_close(arch)
  config.codeVersions[codeVersionId] = CodeVersion(codeVersionId, os.path.basename(code['filename']), archive_get_type(name), description=description)
  _configuration_set(config)
  return {'opState': 'OK', 'codeVersionId': os.path.basename(codeVersionId)}

@expose('GET')
def getConfiguration(kwargs):
  try: check_nofiles(kwargs)
  except ManagerException as e: return {'opState': 'ERROR', 'error': e.message}
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  config = _configuration_get()
  phpconf = {}
  for key in config.php_config.php_conf.defaults:
    if key in config.php_config.php_conf.conf:
      phpconf[key] = config.php_config.php_conf.conf[key]
    else:
      phpconf[key] = config.php_config.php_conf.defaults[key]
  return {'opState': 'OK', 'codeVersionId': config.currentCodeVersion, 'phpconf': phpconf}

@expose('POST')
def updateConfiguration(kwargs):
  try: check_nofiles(kwargs)
  except ManagerException as e: return {'opState': 'ERROR', 'error': e.message}
  
  codeVersionId = None
  if 'codeVersionId' in kwargs:
    codeVersionId = kwargs.pop('codeVersionId')
  phpconf = {}
  config = _configuration_get()
  
  for key in kwargs.keys():
    if not key.startswith('phpconf.') or key[8:] not in config.php_config.php_conf.defaults:
      return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, key).message}
    phpconf[key[8:]] = kwargs.pop(key)
  
  if len(kwargs) != 0:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_UNEXPECTED, kwargs.keys()).message}
  
  if codeVersionId == None and  not phpconf:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_MISSING, 'at least one of "codeVersionId" or "phpconf.n.key" and phpconf.n.value pairs').message}
  
  if codeVersionId and codeVersionId not in config.codeVersions:
    return {'opState': 'ERROR', 'error': ManagerException(E_ARGS_INVALID, detail='Invalid codeVersionId').message}
  
  dstate = _state_get()
  if dstate == S_INIT or dstate == S_STOPPED:
    if codeVersionId: config.currentCodeVersion = codeVersionId
    for key in phpconf:
      config.php_config.php_conf.conf[key] = phpconf[key]
    _configuration_set(config)
  elif dstate == S_RUNNING:
    _state_set(S_ADAPTING, msg='Updating configuration')
    Thread(target=do_updateConfiguration, args=[config, codeVersionId, phpconf]).start()
  else:
    return {'opState': 'ERROR', 'error': ManagerException(E_STATE_ERROR).message}
  return {'opState': 'OK'}

def do_updateConfiguration(config, codeVersionId, phpconf):
  if phpconf:
    for key in phpconf:
      config.php_config.php_conf.conf[key] = phpconf[key]
    for serviceNode in config.getPHPServiceNodes():
      try: client.updatePHP(serviceNode.ip, 5555, config.php_config.port, config.php_config.scalaris, config.php_config.php_conf.conf)
      except client.AgentException as e:
        logger.exception('Failed to update php at node %s' % str(serviceNode))
        _state_set(S_ERROR, msg='Failed to update php at node %s' % str(serviceNode))
        return
  
  if codeVersionId != None:
    for serviceNode in config.serviceNodes.values():
      try: client.updateCode(serviceNode.ip, 5555, codeVersionId, config.codeVersions[codeVersionId].type, os.path.join(code_repo, codeVersionId))
      except client.AgentException as e:
        logger.exception('Failed to update code at node %s' % str(serviceNode))
        _state_set(S_ERROR, msg='Failed to update code at node %s' % str(serviceNode))
        return
    config.currentCodeVersion = codeVersionId
    for serviceNode in config.getProxyServiceNodes():
      try: client.updateHttpProxy(serviceNode.ip, 5555, config.proxy_config.port, config.proxy_config.web_backends, config.currentCodeVersion)
      except client.AgentException as e:
        logger.exception('Failed to update proxy at node %s' % str(serviceNode))
        _state_set(S_ERROR, msg='Failed to update proxy at node %s' % str(serviceNode))
        return
  
  _state_set(S_RUNNING)
  _configuration_set(config)

@expose('GET')
def getHighLevelMonitoring(kwargs):
  return {'opState': 'OK',
          'request_rate': 0,
          'error_rate': 0,
          'throughput': 0,
          'response_time': 0,
          }

@expose('GET')
def getLog(kwargs):
  try:
    fd = open(logfile)
    ret = ''
    s = fd.read()
    while s != '':
      ret += s
      s = fd.read()
    if s != '':
      ret += s
    return {'opState': 'OK', 'log': ret}
  except:
    return {'opState': 'ERROR', 'error': 'Failed to read log'}

@expose('GET')
def getStateChanges(kwargs):
  return {'opState': 'OK', 'state_log': state_log}

def createInitialCodeVersion():
  config = _configuration_get()
  if not os.path.exists(code_repo):
    os.makedirs(code_repo)
  
  fileno, path = tempfile.mkstemp()
  fd = os.fdopen(fileno, 'w')
  fd.write('''<html>
<head>
<title>Welcome to ConPaaS!</title>
</head>
<body bgcolor="white" text="black">
<center><h1>Welcome to ConPaaS!</h1></center>
</body>
</html>''')
  fd.close()
  os.chmod(path, stat.S_IROTH | stat.S_IXOTH)
  
  if len(config.codeVersions) > 0: return
  tfile = tarfile.TarFile(name=os.path.join(code_repo,'code-default'), mode='w')
  tfile.add(path, 'index.html')
  tfile.close()
  os.remove(path)
  config.codeVersions['code-default'] = CodeVersion('code-default', 'code-default.tar', 'tar', description='Initial version')
  config.currentCodeVersion = 'code-default'
  _configuration_set(config)

def registerScalaris(scalaris):
  config = _configuration_get()
  config.php_config.scalaris = scalaris
  _configuration_set(config)

