import os
import re
import tempfile
from uuid import uuid4

from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

HASH_RE = re.compile('^[a-z0-9]{32}$')

class FileUploads(object):
    @mlog
    def get_hash(self):
        hash = uuid4().hex
        path = self.get_path(hash)
        with open(path, 'w'):
            pass
        
        return hash
    
    @mlog
    def get_path(self, hash):
        return os.path.join(tempfile.gettempdir(), 'upload_%s' % hash)
    
    @mlog
    def valid(self, hash):
        return HASH_RE.match(hash)
    
    @mlog
    def exists(self, hash):
        if self.valid(hash):
            path = self.get_path(hash)
            return os.path.exists(path)
    
    @mlog
    def open(self, hash, mode):
        if self.valid(hash):
            path = self.get_path(hash)
            return open(path, mode)
    
    @mlog
    def delete(self, hash):
        if self.valid(hash):
            path = self.get_path(hash)
            
            try:
                os.remove(path)
            except:
                pass
