import unittest

from conpaasdb.libcloudcontrib.opennebula.template import OneTemplate

class Test(unittest.TestCase):
    def test_one_template(self):
        tpl = dict(
            name = 'name',
            cpu = 0.2,
            memory = 512,
            os = dict(
                arch = 'i686',
            ),
            disk = dict(
                image_id = 86,
                readonly = False,
                readwrite = True
            ),
            nic = dict(
                network_id = 24
            )
        )
        
        serialized = str(OneTemplate(tpl))
        
        self.assertEqual(serialized, '''\
name = "name"
memory = 512
nic = [
    network_id = 24
]
disk = [
    readwrite = "yes",
    image_id = 86,
    readonly = "no"
]
os = [
    arch = "i686"
]
cpu = 0.2''')
