import unittest

from conpaasdb.libcloudcontrib.utils import SSHKeygen

class Test(unittest.TestCase):
    def test_ssh_keygen(self):
        kg = SSHKeygen()
        
        self.failUnless(kg.private_key())
        self.failUnless(kg.public_key())
