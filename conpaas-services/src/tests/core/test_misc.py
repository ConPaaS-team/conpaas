
import json
import unittest

from conpaas.core.misc import check_arguments
from conpaas.core.misc import is_int, is_string, is_pos_int, is_pos_nul_int
from conpaas.core.misc import is_in_list, is_list, is_dict, is_dict2
from conpaas.core.misc import is_list_dict, is_list_dict2
from conpaas.core.misc import is_uploaded_file
from conpaas.core.https.server import FileUploadField


class TestMisc(unittest.TestCase):

    def test_check_arguments(self):
        ## No parameters
        exp_params = []
        args = {}
        parsed_args = check_arguments(exp_params, args)
        self.assertEqual(parsed_args, [])

        # One single integer parameter
        exp_params = [('name1', is_int)]
        args = {'name1': 3}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, 3)

        # Missing one parameter
        exp_params = [('name1', is_int)]
        args = {}
        self.assertRaises(Exception, check_arguments, exp_params, args)

        # Wrong type
        exp_params = [('name1', is_int)]
        args = {'name1': 'value'}
        self.assertRaises(Exception, check_arguments, exp_params, args)

        # One single string parameter
        exp_params = [('name1', is_string)]
        args = {'name1': 'value'}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, 'value')

        exp_params = [('name1', is_string)]
        args = {'name1': u'value'}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, 'value')

        # An integer when a string was expected
        exp_params = [('name1', is_string)]
        args = {'name1': 3}
        self.assertRaises(Exception, check_arguments, exp_params, args)

        # A positive integer
        exp_params = [('name1', is_pos_int)]
        args = {'name1': 3}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, 3)

        # A positive integer
        exp_params = [('name1', is_pos_int)]
        args = {'name1': -3}
        self.assertRaises(Exception, check_arguments, exp_params, args)

        # A positive integer
        exp_params = [('name1', is_pos_int)]
        args = {'name1': 0}
        self.assertRaises(Exception, check_arguments, exp_params, args)

        # A positive or null integer
        exp_params = [('name1', is_pos_nul_int)]
        args = {'name1': 3}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, 3)

        # A positive or null integer
        exp_params = [('name1', is_pos_nul_int)]
        args = {'name1': -3}
        self.assertRaises(Exception, check_arguments, exp_params, args)

        # A positive or null integer
        exp_params = [('name1', is_pos_nul_int)]
        args = {'name1': 0}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, 0)

        # Extra unknown parameter
        exp_params = [('name1', is_int)]
        args = {'name1': 3, 'name2': 'value'}
        self.assertRaises(Exception, check_arguments, exp_params, args)

        # Default value
        exp_params = [('name1', is_int, 5)]
        args = {}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, 5)

        # Mix of mandatory args and optional ones
        exp_params = [('name1', is_int, 5), ('name2', is_int)]
        args = {'name2': 7}
        name1, name2 = check_arguments(exp_params, args)
        self.assertEqual(name1, 5)
        self.assertEqual(name2, 7)

        # Check uploaded file type
        exp_params = [('uploaded_file', is_uploaded_file)]
        filename = 'myfile.txt'
        filecontent = 'file'
        args = {'uploaded_file': FileUploadField(filename, filecontent)}
        uploaded_file = check_arguments(exp_params, args)
        self.assertEqual(uploaded_file.filename, filename)
        self.assertEqual(uploaded_file.file, filecontent)

        # Check in_list constraint
        exp_params = [('name1', is_in_list([3, 5, 6]))]
        args = {'name1': 6}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, 6)

        # Check not in_list constraint
        exp_params = [('name1', is_in_list([3, 5, 6]))]
        args = {'name1': 1}
        self.assertRaises(Exception, check_arguments, exp_params, args)

        # Check is_list constraint
        exp_params = [('name1', is_list)]
        mylist = [3, 'a']
        args = {'name1': mylist}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, mylist)

        # Check is_dict constraint
        exp_params = [('name1', is_dict)]
        mydict = {'key': 3}
        args = {'name1': mydict}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, mydict)

        # Check is_dict2 constraint
        exp_params = [('name1', is_dict2(["key"]))]
        mydict = {'key': 3}
        args = {'name1': mydict}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, mydict)

        # Check is_dict2 constraint
        exp_params = [('name1', is_dict2(["key"], ["optkey"]))]
        mydict = {'key': 3}
        args = {'name1': mydict}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, mydict)

        # Check is_dict2 constraint: missing mandatory
        exp_params = [('name1', is_dict2(["key"], ["optkey"]))]
        mydict = {'optkey': 3}
        args = {'name1': mydict}
        self.assertRaisesRegexp(Exception, ".*expecting key.*", check_arguments, exp_params, args)

        # Check is_dict2 constraint: extra unknown key
        exp_params = [('name1', is_dict2(["key"], ["optkey"]))]
        mydict = {'key': 42, 'optkey': 3, 'newkey': 'great value'}
        args = {'name1': mydict}
        self.assertRaisesRegexp(Exception, ".*Unexpected key.*", check_arguments, exp_params, args)

        # Check is_list_dict constraint
        exp_params = [('name1', is_list_dict)]
        mylistdict = [{'key': 3}]
        args = {'name1': mylistdict}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, mylistdict)

        # Check is_list_dict2 constraint
        exp_params = [('name1', is_list_dict2(['key']))]
        mylistdict = [{'key': 3}, {'key': 56}]
        args = {'name1': mylistdict}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, mylistdict)

        # Check is_list_dict2 constraint
        exp_params = [('name1', is_list_dict2(['key']))]
        mylistdict = [{'key': 3}, {'key': 56, 'nokey': 42}]
        args = {'name1': mylistdict}
        self.assertRaisesRegexp(Exception, ".*Unexpected key.*", check_arguments, exp_params, args)

        # Try with a JSON conversion first
        # Check is_list constraint
        exp_params = [('name1', is_list)]
        mylist = unicode('[3, "a"]')
        mylist = json.loads(mylist)
        args = {'name1': mylist}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, mylist)

        # Check is_dict constraint
        exp_params = [('name1', is_dict)]
        mydict = unicode('{"key": 3}')
        mydict = json.loads(mydict)
        args = {'name1': mydict}
        name1 = check_arguments(exp_params, args)
        self.assertEqual(name1, mydict)
