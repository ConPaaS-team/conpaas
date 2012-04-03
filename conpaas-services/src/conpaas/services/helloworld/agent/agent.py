from conpaas.core.expose import expose
from conpaas.core.http import HttpJsonResponse, HttpErrorResponse,\
                         HttpFileDownloadResponse, HttpRequest,\
                         FileUploadField, HttpError, _http_post
from conpaas.core.log import create_logger

class HelloWorldAgent():
    def __init__(self,
                 config_parser, # config file
                 **kwargs):     # anything you can't send in config_parser 
                                # (hopefully the new service won't need anything extra)

      self.logger = create_logger(__name__)
      self.state = 'INIT' 
      self.gen_string = config_parser.get('agent', 'STRING_TO_GENERATE')

    @expose('GET')
    def check_agent_process(self, kwargs):
      """Check if agent process started - just return an empty response"""
      if len(kwargs) != 0:
        return HttpErrorResponse('ERROR: Arguments unexpected')
      return HttpJsonResponse()

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
 
