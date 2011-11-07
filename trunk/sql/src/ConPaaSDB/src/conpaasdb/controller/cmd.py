import fabric_threadsafe.patch

import argparse

from conpaasdb.utils.log import get_logger_plus
from conpaasdb.controller.service import ControllerService

logger, flog, mlog = get_logger_plus(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='conpaasdb.conf')
    
    subparsers = parser.add_subparsers(dest='subcommand')

    subparsers.add_parser('manager_list')

    manager_create = subparsers.add_parser('manager_create')
    manager_create.add_argument('-m', '--manager-config', default='manager.conf')
    manager_create.add_argument('-a', '--agent-config', default='agent.conf')

    manager_state = subparsers.add_parser('manager_state')
    manager_state.add_argument('uuid')
    
    manager_info = subparsers.add_parser('manager_info')
    manager_info.add_argument('uuid')
    
    manager_destroy = subparsers.add_parser('manager_destroy')
    manager_destroy.add_argument('uuid')
    
    args = vars(parser.parse_args())
    
    c = ControllerService(args.pop('config'))
    print getattr(c, args.pop('subcommand'))(**args)

if __name__ == '__main__':
    main()
