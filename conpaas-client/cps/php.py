import sys

from web import WebClient

AUTOSCALING_STRATEGIES = ["low", "medium_down", "medium", "medium_up", "high"]


class Client(WebClient):

    def enable_code(self, app_id, service_id, code_version):
        params = { 'codeVersionId': code_version }

        res = self.callmanager(app_id, service_id, "update_php_configuration", 
            True, params)

        if 'error' in res:
            print res['error']

        else:
            print code_version, 'enabled'

    def toggle_debug(self, app_id, service_id):
        conf = self.callmanager(app_id, service_id, 'get_configuration', False, {})
        debug_mode = conf['phpconf']['display_errors']

        params = { 'phpconf': {} }

        if debug_mode == 'On':
            params['phpconf']['display_errors'] = 'Off'
        else:
            params['phpconf']['display_errors'] = 'On'

        res = self.callmanager(app_id, service_id, "update_php_configuration", 
            True, params)

        if 'error' in res:
            print res['error']
        else:
            conf = self.callmanager(app_id, service_id, 'get_configuration', False, {})
            print 'Debug mode is now', conf['phpconf']['display_errors']

    def usage(self, aid, sid):
        WebClient.usage(self, aid, sid)
        print ""
        print "    ----Service specific commands-------"
        print ""
        print "    toggle_debug     appid  serviceid                                                      # enable/disable debug mode" 
        print "    on_autoscaling   appid  serviceid  adapt_interval  response_time_objective  strategy   #  enable autoscaling"
        print "    off_autoscaling  appid  serviceid                                                      #  disable autoscaling"

    def on_autoscaling(self, app_id, service_id, cool_down, response_time, strategy):
        args = {'cool_down': cool_down,
                'response_time': response_time,
                'strategy': strategy,
                }
        res = self.callmanager(app_id, service_id, 'on_autoscaling', True, args)
        if 'error' in res:
            print "Error: %s" % res['error']

    def off_autoscaling(self, app_id, service_id):
        res = self.callmanager(app_id, service_id, 'off_autoscaling', True, {})
        if 'error' in res:
            print "Error: %s" % res['error']

    def main(self, argv):
        WebClient.main(self, argv)

        command = argv[1]

        if command in ['toggle_debug', 'on_autoscaling', 'off_autoscaling']:
            # second argument must be the service identifier
            try:
                aid = int(argv[2])
                sid = int(argv[3]) 
            except IndexError:
                print "Error: missing service identifier to command %s." % command
                sys.exit(1)
            except ValueError:
                print "Error: arguments '%s and %s' are not valid service identifiers." % (argv[2], argv[3])
                sys.exit(1)

        if command == 'toggle_debug':
            self.toggle_debug(aid, sid)

        elif command == 'on_autoscaling':
            if len(argv) < 6:
                print "Error: missing arguments to command %s." % command
            try:
                cool_down = int(argv[4])
            except ValueError:
                print "Error: argument adapt_interval must be an integer (time in minutes)."
                sys.exit(1)
            try:
                response_time = int(argv[5])
            except ValueError:
                print "Error: argument response_time_objective must be an integer (time in milliseconds)."
                sys.exit(1)
            strategy = argv[6]
            if strategy not in AUTOSCALING_STRATEGIES:
                print "Error: argument strategy must be one of %s." % AUTOSCALING_STRATEGIES
                sys.exit(1)
            self.on_autoscaling(aid, sid, cool_down, response_time, strategy)

        elif command == 'off_autoscaling':
            self.off_autoscaling(aid, sid)
