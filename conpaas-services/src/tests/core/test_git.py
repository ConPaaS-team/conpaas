import tempfile, os, os.path

import re
import unittest

from conpaas.core import git
from conpaas.core.misc import run_cmd

class TestGit(unittest.TestCase):

    def setUp(self):
        git.AUTH_KEYS_FILENAME = "/tmp/conpaas_git_authorized_keys"
        open(git.AUTH_KEYS_FILENAME, 'w').write("")

        if not run_cmd("git config --get user.email"):
            run_cmd("git config --global user.email info@conpaas.eu")

        if not run_cmd("git config --get user.name"):
            run_cmd("git config --global user.name ConPaaS")

    def test_01_empty_authorized_keys(self):
        # get_authorized_keys should return 0 with an empty file
        self.assertEquals(0, len(git.get_authorized_keys()))

    def test_02_add_authorized_keys(self):
        new_keys = [ "ssh-rsa test123 ema@uranus" ]

        # add_authorized_keys should return 1 on successful insertion
        self.assertEquals(1, git.add_authorized_keys(new_keys))

        # add_authorized_keys should return 0 if the key is already present
        self.assertEquals(0, git.add_authorized_keys(new_keys))

        # we should now have exactly 1 authorized key
        self.assertEquals(1, len(git.get_authorized_keys()))

        # adding a new one
        self.assertEquals(1, git.add_authorized_keys([ "ssh-rsa test ema@mars" ]))

        # we should now have exactly 2 authorized keys
        self.assertEquals(2, len(git.get_authorized_keys()))

    def test_03_remove_authorized_keys(self):
        # 0 keys left in a empty authorized_keys
        self.assertEquals(0, git.remove_authorized_keys([]))        

        # adding one key
        self.assertEquals(1, git.add_authorized_keys([ "ssh-rsa test ema@mars" ]))

        # we should now have exactly 1 authorized key
        self.assertEquals(1, len(git.get_authorized_keys()))

        # adding another key
        self.assertEquals(1, git.add_authorized_keys([ "ssh-rsa test2 ema@mars" ]))

        # we should now have exactly 2 authorized keys
        self.assertEquals(2, len(git.get_authorized_keys()))

        # adding another key
        self.assertEquals(1, git.add_authorized_keys([ "ssh-rsa test3 ema@mars" ]))

        # we should now have exactly 3 authorized keys
        self.assertEquals(3, len(git.get_authorized_keys()))

        # removing a single key should leave us with 2 keys
        self.assertEquals(2, git.remove_authorized_keys([ "ssh-rsa test2 ema@mars" ]))

        # we should now have exactly 2 authorized keys
        self.assertEquals(2, len(git.get_authorized_keys()))

        # removing the two remaining keys
        self.assertEquals(0, git.remove_authorized_keys(
                [ "ssh-rsa test ema@mars", "ssh-rsa test3 ema@mars" ]
        ))

        # we should now have no authorized_key left
        self.assertEquals(0, len(git.get_authorized_keys()))

    def test_05_git_code_version(self):
        repo = git.git_create_tmp_repo() 
        code_version = git.git_code_version(repo)
        print "XXX_05", code_version

        # git_code_version should be something like '68ed1b0'
        pattern = "^[a-z0-9]{7,7}$"
        self.assertIsNot(None, re.match(pattern, code_version), 
            "code_version '%s' does not match '%s'" % (code_version, pattern))

    def test_06_git_last_description(self):
        repo = git.git_create_tmp_repo() 
        self.assertEquals("Initial commit", git.git_last_description(repo))

    def test_07_git_enable_revision(self):
        target_dir = tempfile.mkdtemp()
        repo = git.git_create_tmp_repo()
        rev = git.git_code_version(repo) 
        print "XXX_07", rev

        dest_dir = git.git_enable_revision(target_dir, repo, rev)

        self.assertEquals(rev, os.path.basename(dest_dir))

if __name__ == "__main__":
    unittest.main()
