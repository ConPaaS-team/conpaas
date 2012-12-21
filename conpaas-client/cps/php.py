import sys

from web import WebClient

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

    def main(self, argv):
        WebClient.main(self, argv)

        command = argv[1]

        if command == 'toggle_debug':
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            self.toggle_debug(sid)
