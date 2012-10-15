import os
import sys

dirname = os.path.dirname(__file__)

sys.path.insert(0, dirname)

activate_this = os.path.join(dirname, "bin", "activate_this.py")
execfile(activate_this, dict(__file__=activate_this))

from app import app as application
