from StringIO import StringIO

from fabric.api import *

def run_complex(code, *args, **kwargs):
    tmp = str(run('mktemp'))
    f = StringIO(code)
    put(f, tmp)
    return run('bash %s' % tmp, *args, **kwargs)
