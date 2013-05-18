from web import WebClient

class Client(WebClient):

    def enable_code(self, service_id, code_version):
        params = { 'codeVersionId': code_version }

        res = self.callmanager(service_id, "update_java_configuration", 
            True, params)

        if 'error' in res:
            print res['error']

        else:
            print code_version, 'enabled'
