from argparse import ArgumentParser
import ConfigParser
import logging
import os
import sys

CONF_FILE = "cps-tools.conf"


class CpsParser(ArgumentParser):

    def __init__(self, *args, **kwargs):
       ArgumentParser.__init__(self, *args, **kwargs)

    # Override this method to print the parser's error messages in the usual format
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write('ERROR: %s\n' % message)
        sys.exit(2)


def config(description, logger):
    # Turn off help, so we print all options in response to -h
    parser = CpsParser(add_help=False,)
    parser.add_argument('-d', '--debug', action='store_true',
                        help="Display debug messages.")
    parser.add_argument("--conf_file", help="Specify a configuration file",
                        metavar="FILE")

    args, remaining_argv = parser.parse_known_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.conf_file:
        config_files = [os.path.expanduser(args.conf_file)]
    else:
        sys_confdir = '/etc/cps-tools/'
        user_confdir = os.path.join(os.environ['HOME'], ".conpaas")
        config_files = [os.path.join(sys_confdir, CONF_FILE),
                        os.path.join(user_confdir, CONF_FILE)]

    config_parser = ConfigParser.SafeConfigParser()
    read_files = config_parser.read(config_files)

    unread_files = [f for f in config_files if f not in read_files]
    logger.info("Configuration files successfully read are: %s" % read_files)
    if unread_files != []:
        errors = "\n"
        for f in unread_files:
            try:
                open(f)
            except:
                ex = sys.exc_info()[1]
                errors += "%s\n" % ex
        logger.info("Skipping configuration files that cannot be read: %s" % errors)

    cps_tools_section = "cps-tools"
    conf_values = dict()
    if config_parser.has_section(cps_tools_section):
        expected_options = ['director_url', 'username', 'password', 'debug']
        other_options = [o for o in config_parser.options(cps_tools_section)
                         if o not in expected_options]
        if other_options != []:
            logger.warning('Skipping unknown options from section "%s": %s'
                           % (cps_tools_section, other_options))
        for option in expected_options:
            if config_parser.has_option(cps_tools_section, option):
                conf_values[option] = config_parser.get(cps_tools_section, option)
        conf_values = dict(config_parser.items(cps_tools_section))

    other_sections = [s for s in config_parser.sections() if s != cps_tools_section]
    if other_sections != []:
        logger.warning('Skipping unknown sections of configuration files: %s'
                       % other_sections)

    parser = CpsParser(description=description, parents=[parser],
                       epilog="See %s <command> -h' for more information on a specific command."
                       % sys.argv[0])

    parser.add_argument('--director_url', metavar='URL',
                        help='ConPaaS\'s director URL')
    parser.add_argument('--username', help='ConPaaS user name')
    parser.add_argument('--password', help='ConPaaS user password')
    if args.debug:
        conf_values['debug'] = args.debug
    elif 'debug' in conf_values:
        confdebug = conf_values['debug'].lower()
        if confdebug == 'true':
            conf_values['debug'] = True
        elif confdebug == 'false':
            conf_values['debug'] = False
        else:
            errmsg = "Option 'debug' in configuration file cps-tools.conf must be 'true' or 'false'."
            logger.error(errmsg)
            raise Exception(errmsg)
    else:
        conf_values['debug'] = False
    parser.set_defaults(**conf_values)

    return parser, remaining_argv
