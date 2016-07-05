class DirectorCmd:

    def __init__(self, parser, client):
        self.client = client

        self.subparsers = parser.add_subparsers(help=None, title=None,
                                                description=None,
                                                metavar="<sub-command>")
        self._add_version()
        self._add_help(parser)

    def add_parser(self, *args, **kwargs):
        return self.subparsers.add_parser(*args, **kwargs)

    # ========== help
    def _add_help(self, parser):
        subparser = self.add_parser('help', help="show help")
        subparser.set_defaults(run_cmd=self.user_help, parser=parser)

    def user_help(self, args):
        args.parser.print_help()

    # ========== version
    def _add_version(self):
        subparser = self.add_parser('version', help="show director's version")
        subparser.set_defaults(run_cmd=self.version, parser=subparser)

    def version(self, _args):
        version = self.client.call_director_get("version")
        print "ConPaaS director version %s" % version
