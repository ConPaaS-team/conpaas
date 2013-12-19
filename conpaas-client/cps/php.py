import sys

from web import WebClient

AUTOSCALING_STRATEGIES = ["low", "medium_down", "medium", "medium_up", "high"]


class Client(WebClient):

    def enable_code(self, service_id, code_version):
        params = { 'codeVersionId': code_version }

        res = self.callmanager(service_id, "update_php_configuration", 
            True, params)

        if 'error' in res:
            print res['error']

        else:
            print code_version, 'enabled'

    def toggle_debug(self, service_id):
        conf = self.callmanager(service_id, 'get_configuration', False, {})
        debug_mode = conf['phpconf']['display_errors']

        params = { 'phpconf': {} }

        if debug_mode == 'On':
            params['phpconf']['display_errors'] = 'Off'
        else:
            params['phpconf']['display_errors'] = 'On'

        res = self.callmanager(service_id, "update_php_configuration", 
            True, params)

        if 'error' in res:
            print res['error']
        else:
            conf = self.callmanager(service_id, 'get_configuration', False, {})
            print 'Debug mode is now', conf['phpconf']['display_errors']

    def usage(self, cmdname):
        WebClient.usage(self, cmdname)
        print "    toggle_debug      serviceid           # enable/disable debug mode" 
        print "    on_autoscaling  serviceid  adapt_interval  response_time_objective  strategy   #  enable autoscaling"
        print "    off_autoscaling  serviceid             #  disable autoscaling"

    def on_autoscaling(self, service_id, cool_down, response_time, strategy):
        args = {'cool_down': cool_down,
                'response_time': response_time,
                'strategy': strategy,
                }
        res = self.callmanager(service_id, 'on_autoscaling', True, args)
        if 'error' in res:
            print "Error: %s" % res['error']

    def off_autoscaling(self, service_id):
        res = self.callmanager(service_id, 'off_autoscaling', True, {})
        if 'error' in res:
            print "Error: %s" % res['error']

    def main(self, argv):
        WebClient.main(self, argv)

        command = argv[1]

        if command in ['toggle_debug', 'on_autoscaling', 'off_autoscaling']:
            # second argument must be the service identifier
            try:
                sid = int(argv[2])
            except IndexError:
                print "Error: missing service identifier to command %s." % command
                sys.exit(1)
            except ValueError:
                print "Error: argument '%s' is not a service identifier." % argv[2]
                sys.exit(1)

        if command == 'toggle_debug':
            self.toggle_debug(sid)

        elif command == 'on_autoscaling':
            if len(argv) < 6:
                print "Error: missing arguments to command %s." % command
            try:
                cool_down = int(argv[3])
            except ValueError:
                print "Error: argument adapt_interval must be an integer (time in minutes)."
                sys.exit(1)
            try:
                response_time = int(argv[4])
            except ValueError:
                print "Error: argument response_time_objective must be an integer (time in milliseconds)."
                sys.exit(1)
            strategy = int(argv[5])
            if strategy not in AUTOSCALING_STRATEGIES:
                print "Error: argument strategy must be one of %s." % AUTOSCALING_STRATEGIES
                sys.exit(1)
            self.on_autoscaling(sid, cool_down, response_time, strategy)

        elif command == 'off_autoscaling':
            self.off_autoscaling(sid)

        else:
            print "Error: unknown sub-command '%s'." % command
