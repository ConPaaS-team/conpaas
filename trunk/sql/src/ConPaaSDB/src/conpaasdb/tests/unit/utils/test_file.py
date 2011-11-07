import unittest
import os

from conpaasdb.utils.file import FileUploads

class Test(unittest.TestCase):
    def test_file_uploads(self):
        fu = FileUploads()
        
        hash = fu.get_hash()
        
        path = fu.get_path(hash)
        
        self.failUnless(os.path.exists(path))
        
        self.failUnless(fu.valid('df20251dab594b62be0ef374a30235d2'))
        self.failUnless(fu.valid('e4d14da7ad2d472980a9bb8731638f8c'))
        
        self.failIf(fu.valid('../etc/passwd'))
        self.failIf(fu.valid('/tmp'))
        
        self.failUnless(fu.exists(hash))
        
        file = fu.open(hash, 'r')
        file.close()
        
        fu.delete(hash)
        
        self.failIf(fu.exists(hash))
