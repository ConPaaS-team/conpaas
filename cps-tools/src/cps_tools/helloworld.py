from .service import ServiceCmd


class HelloWorldCmd(ServiceCmd):

    def __init__(self, helloworld_parser, client):
        ServiceCmd.__init__(self, helloworld_parser, client, "helloworld",
                            ['node'], "HelloWorld service sub-commands help")
        self._add_get_helloworld()

    # ========== get_helloworld
    def _add_get_helloworld(self):
        subparser = self.add_parser('get_helloworld',
                                    help="test function of the HelloWorld service")
        subparser.set_defaults(run_cmd=self.get_helloworld, parser=subparser)
        subparser.add_argument('app_name_or_id',
                               help="Name or identifier of an application")
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def get_helloworld(self, args):
        app_id, service_id = self.get_service_id(args.app_name_or_id, args.serv_name_or_id)
        res = self.client.call_manager(app_id, service_id, "get_helloworld", False, {})
        if 'error' in res:
            self.client.error(res['error'])
        else:
            print res['helloworld']
