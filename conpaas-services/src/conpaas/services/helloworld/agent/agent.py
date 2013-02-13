from conpaas.core.expose import expose

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse

from conpaas.core.agent import BaseAgent

class HelloWorldAgent(BaseAgent):
    def __init__(self,
                 config_parser, # config file
                 **kwargs):     # anything you can't send in config_parser 
                                # (hopefully the new service won't need anything extra)
      BaseAgent.__init__(self, config_parser)
      self.gen_string = config_parser.get('agent', 'STRING_TO_GENERATE')

    @expose('POST')
    def startup(self, kwargs):
      self.state = 'RUNNING'
      self.logger.info('Agent started up')
      return HttpJsonResponse()

    @expose('GET')
    def get_helloworld(self, kwargs):
      if self.state != 'RUNNING':
        return HttpErrorResponse('ERROR: Wrong state to get_helloworld')
      return HttpJsonResponse({'result':self.gen_string})
 
