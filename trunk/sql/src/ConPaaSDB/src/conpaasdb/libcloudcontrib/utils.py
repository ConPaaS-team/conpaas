import paramiko
import base64
from StringIO import StringIO
import tempfile

class SSHKeygen(object):
    def __init__(self):
        self.rsakey = paramiko.RSAKey.generate(2048)
        
    def _public_key(self):
        return base64.b64encode(str(self.rsakey))
    
    def public_key(self):
        return 'ssh-rsa %s user@host' % self._public_key()
    
    def private_key(self):
        fp = StringIO()
        self.rsakey.write_private_key(fp)
        return fp.getvalue()
    
    def private_key_file(self):
        filename = tempfile.mktemp()
        self.rsakey.write_private_key_file(filename)
        return filename
