from cps.base import BaseClient

class Client(BaseClient):

    def info(self, service_id):
        BaseClient.info(self, service_id)

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
