from conpaas.mysql.utils.log import get_logger_plus, get_logger
from conpaas.mysql.adapters.mysql import MySQLSettings

logger, flog, mlog = get_logger_plus(__name__)

class MySQLConfig(object):
    mysql_settings = MySQLSettings
    
    @mlog
    def __init__(self, filename="/etc/mysqld/my.cnf"):
        self.config_file = filename
        logger.debug("Using filename %s" % self.config_file)
        self.sections = []
        self.options = {}
        self.load()        
    
    @mlog
    def set(self, section, key, value):
        self.options[(section, key)] = value
    
    @mlog 
    def load(self):
        logger.debug("Loading configuration from %s" % self.config_file)
        with open(self.config_file) as f:
            lines = f.readlines()
        cur_sec = None      
        for line in lines:
            strip = line.strip()
            if not strip.startswith('#'):                
                if strip.startswith('['):
                    cur_sec = strip.strip('[]')
                    self.sections.append(cur_sec)                
                else:
                    pair = [x.strip() for x in strip.split('=', 1)] + [None]
                    cur_key, cur_val = pair[:2]
                    #print("pair: %s, %s, %s" % (cur_sec, cur_key, cur_val))
                    if cur_val:
                        try:
                            self.set(cur_sec, cur_key, cur_val)
                        except:
                            pass
                    else:
                        if cur_sec and cur_key:
                            self.set(cur_sec, cur_key, "")   
    
    @mlog
    def save_asnew_config(self, filename="/etc/mysqld/my.cnf"):
        logger.debug("Saving new configuration to %s " % filename)        
        if filename == None:
            filename = self.config_file
        with open(filename, 'w') as f:
            for section in self.sections:
                line = "[%s]\n" % section
                f.write(line)
                for (sec,key) in self.options:   
                    if sec == section:                 
                        if key and self.options[(section,key)]:
                            line = ("%s = %s\n")%(key, self.options[(section,key)])                        
                        elif key:
                            line = ("%s\n")%(key)
                        f.write(line)
    
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
