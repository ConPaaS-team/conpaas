import unittest

import tempfile
import colander as cl

from conpaasdb.utils.config import is_url, ConfigContainer, get_config

class Test(unittest.TestCase):
    def test_is_url(self):
        is_url(None, 'http://www.example.com')
        is_url(None, 'http://user:pass@www.example.com')
        
        self.assertRaises(cl.Invalid, is_url, None, 'http://')
        self.assertRaises(cl.Invalid, is_url, None, 'foo.bar')
        self.assertRaises(cl.Invalid, is_url, None, 'ftp://foo.bar')
    
    def test_config_container(self):
        cc = ConfigContainer({
            'section': {
                'key': 'value',
                'subsection': {
                    'subkey': 'subvalue'
                }
            }
        })
        
        self.failUnless(cc.section)
        self.assertEqual(cc.section.key, 'value')
        self.failUnless(cc.section.subsection)
        self.assertEqual(cc.section.subsection.subkey, 'subvalue')
    
    def test_get_config(self):
        tmp = tempfile.mktemp()
        
        with open(tmp, 'w') as f:
            f.write('''\
[section1]
key1 = value1
key2 =  

[section2]
string = value
int = 3
bool = true
float = 4.2
url = http://www.example.com
    ''')
        
        class Section1(cl.Schema):
            key1 = cl.SchemaNode(cl.Str())
            key2 = cl.SchemaNode(cl.Str(), missing=None)
        
        class Section2(cl.Schema):
            string = cl.SchemaNode(cl.Str())
            int = cl.SchemaNode(cl.Int())
            bool = cl.SchemaNode(cl.Bool())
            float = cl.SchemaNode(cl.Float())
            url = cl.SchemaNode(cl.Str(), validator=is_url)
        
        class TestSchema(cl.Schema):
            section1 = Section1()
            section2 = Section2()
        
        config = get_config(tmp, TestSchema)
        
        self.assertEqual(config.section1.key1, 'value1')
        self.assertFalse(config.section1.key2)
        self.assertEqual(config.section2.string, 'value')
        self.assertEqual(config.section2.int, 3)
        self.assertEqual(config.section2.bool, True)
        self.assertEqual(config.section2.float, 4.2)
        self.assertEqual(config.section2.url, 'http://www.example.com')
