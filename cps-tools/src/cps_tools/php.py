
import argcomplete
import logging
import os
import sys

from .base import BaseClient
from .config import config
from .web import WebCmd


class PHPCmd(WebCmd):

    def __init__(self, php_parser, client):
        WebCmd.__init__(self, php_parser, client, "php",
                        "PHP server sub-commands help")
        self._add_enable_code()
        self._add_get_configuration()
        self._add_debug()

    # ========== enable_code
    def _add_enable_code(self):
        subparser = self.add_parser('enable_code',
                                    help="select PHP code to enable")
        subparser.set_defaults(run_cmd=self.enable_code, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('code_version', help="Code version")

    def enable_code(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        code_version = args.code_version
        params = {'codeVersionId': code_version}

        res = self.client.call_manager_post(service_id,
                                            "update_php_configuration",
                                            params)
        if 'error' in res:
            print res['error']
        else:
            print code_version, 'enabled'

    # ========== get_configuration
    def _add_get_configuration(self):
        subparser = self.add_parser('get_configuration',
                                    help="return the PHP configuration")
        subparser.set_defaults(run_cmd=self.get_configuration, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")

    def get_configuration(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        conf = self.client.call_manager_get(service_id, 'get_configuration')
        if 'error' in conf:
            self.client.error("Cannot get configuration for PHP service: %s."
                              % conf['error'])
        print "%s" % conf

    # ========== debug
    def _add_debug(self):
        subparser = self.add_parser('debug',
                                    help="enable or disable debug mode")
        subparser.set_defaults(run_cmd=self.debug, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('on_off', choices=['on', 'off'],
                               help="'on' or 'off'")

    def debug(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        debug_mode = args.on_off.capitalize()
        if debug_mode != 'On' and debug_mode != 'Off':
            self.client.error("Expecting 'on' or 'off' for argument on_off."
                              " Argument was '%s'" % args.on_off)
        params = {'phpconf': {}}
        params['phpconf']['display_errors'] = debug_mode

        res = self.client.call_manager_post(service_id,
                                            "update_php_configuration",
                                            params)
        if 'error' in res:
            self.client.error("Could not set debug mode to %s: %s"
                              % (args.on_off, res['error']))

    # ========== migrate_nodes
    def _add_migrate_nodes(self):
        subparser = self.add_parser('migrate_nodes',
                                    help="migrate nodes between clouds")
        subparser.set_defaults(run_cmd=self.migrate_nodes, parser=subparser)
        subparser.add_argument('serv_name_or_id',
                               help="Name or identifier of a service")
        subparser.add_argument('migration_plan',
                               help="description of migration")
        subparser.add_argument('--delay',
                               help="Delay the removal of original nodes after a successful node creation")

    def migrate_nodes(self, args):
        service_id = self.get_service_id(args.serv_name_or_id)
        params = {'codeVersionId': args.version}

        res = self.client.call_manager_get(service_id, "migrate_nodes",
                                           params)

        if 'error' in res:
            self.client.error("Cannot download code: %s" % res['error'])

        else:
            destfile = os.path.join(os.getenv('TMPDIR', '/tmp'), args.version) + '.tar.gz'
            open(destfile, 'w').write(res)
            print destfile, 'written'


def main():
    logger = logging.getLogger(__name__)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    cmd_client = BaseClient(logger)

    parser, argv = config('Manage ConPaaS PHP services.', logger)

    _serv_cmd = PHPCmd(parser, cmd_client)

    argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)
    cmd_client.set_config(args.director_url, args.username, args.password,
                          args.debug)
    try:
        args.run_cmd(args)
    except:
        e = sys.exc_info()[1]
        sys.stderr.write("ERROR: %s\n" % e)
        sys.exit(1)

if __name__ == '__main__':
    main()
