class FakeSupervisor(object):
    def start(self, name):
        return True
    
    def stop(self, name):
        return True
    
    def info(self, name):
        return {
            'description': 'pid 2001, uptime 14:59:20',
            'exitstatus': 0,
            'group': name,
            'logfile': '/var/log/supervisor/mysqld-stdout---supervisor-ly7INR.log',
            'name': name,
            'now': 1315548883,
            'pid': 2001,
            'spawnerr': '',
            'start': 1315494923,
            'state': 20,
            'statename': 'RUNNING',
            'stderr_logfile': '/var/log/supervisor/mysqld-stderr---supervisor-hWGi9g.log',
            'stdout_logfile': '/var/log/supervisor/mysqld-stdout---supervisor-ly7INR.log',
            'stop': 1315494916
        }
