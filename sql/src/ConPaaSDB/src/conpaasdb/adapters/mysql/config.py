import inject

from conpaasdb.adapters.mysql import MySQLSettings
from conpaasdb.utils.log import get_logger_plus

logger, flog, mlog = get_logger_plus(__name__)

class MySQLConfig(object):
    mysql_settings = inject.attr(MySQLSettings)
    
    @mlog
    def __init__(self):
        self.config_file = self.mysql_settings.config
        
        self.options = {}
    
    @mlog
    def set(self, section, key, value):
        self.options[(section, key)] = value
    
    @mlog
    def save(self):
        with open(self.config_file) as f:
            lines = f.readlines()
        
        section = None
        
        with open(self.config_file, 'w') as f:
            for line in lines:
                strip = line.strip()
                if strip.startswith('['):
                    section = strip.strip('[]')
                else:
                    key = strip.split('=')[0].strip()
                    value = self.options.get((section, key), None)
                    if value:
                        value = self.options[(section, key)]
                        line = '%s = %s\n' % (key, value)
                
                f.write(line)
    
    @mlog
    def get(self, section, key, typ=None):
        with open(self.config_file) as f:
            lines = f.readlines()
        
        cur_sec = None
        
        for line in lines:
            strip = line.strip()
            if strip.startswith('['):
                cur_sec = strip.strip('[]')
            else:
                pair = [x.strip() for x in strip.split('=', 1)] + [None]
                cur_key, cur_val = pair[:2]
                
                if (cur_sec, cur_key) == (section, key) and cur_val:
                    if typ:
                        try:
                            return typ(cur_val)
                        except:
                            pass
                    
                    return cur_val
