import jsonrpclib
import requests
import urlparse

from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class ClientBase(object):
    @mlog
    def __init__(self, host, port=60000):
        self.service_url = 'http://%s:%s/' % (host, int(port))
        
        self.service = jsonrpclib.Server(self.service_url)
    
    @mlog
    def upload_file(self, file):
        upload_hash = self.service.upload()
        url = urlparse.urljoin(self.service_url, '/upload/%s' % upload_hash)
        requests.post(url, open(file, 'rb').read())
        return upload_hash
