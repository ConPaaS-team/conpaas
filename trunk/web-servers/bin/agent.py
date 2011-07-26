'''
Created on Jul 4, 2011

@author: ielhelw
'''
from conpaas.web.agent.server import AgentServer

if __name__ == '__main__':
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option('-p', '--port', type='int', default=5555, dest='port')
  parser.add_option('-b', '--bind', type='string', default='0.0.0.0', dest='address')
  options, args = parser.parse_args()
  print options.address, options.port
  agent = AgentServer((options.address, options.port))
  agent.serve_forever()
