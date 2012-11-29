import sys

from web import WebClient

class Client(WebClient):

    def enable_code(self, service_id, code_version):
        print 'java'
