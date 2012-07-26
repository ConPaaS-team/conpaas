#!/usr/bin/python

import logging
from optparse import OptionParser
import os
import subprocess
import time

import app
from edge import EdgeLocation, NetworkSnapshot


class RemoteCommand:

    def __init__(self, host):
        self.runner = '/usr/local/cds/run_command.sh'
        self.host = host

    def run(self, command, *args):
        cmd_args = [self.runner, self.host, command]
        if args:
            cmd_args.extend(list(args))
        subprocess.check_call(cmd_args)


class ConfMonitor:

    def __init__(self, apps_dir):
        self.apps_dir = apps_dir
        self.snapshot = NetworkSnapshot()
        self.check_interval = self.snapshot.interval
        self.apps = {}
        self.logger = logging.getLogger('conf-monitor')

    def get_apps(self):
        self.apps = app.read_apps(self.apps_dir)
        self.apps_set = set(self.apps.keys())

    def link_app(self, cmd, app):
        try:
            cmd.run('link_app', app)
            self.logger.info('%s added to %s' % (app, cmd.host))
        except:
            self.logger.error('Could not add app %s to %s' % (app, cmd.host))

    def remove_app(self, cmd, app):
        try:
            cmd.run('rm_app', app)
            self.logger.info('%s removed from %s' % (app, cmd.host))
        except:
            self.logger.error('Could not remove app %s from %s' % (app, cmd.host))

    def check(self, edge_location):
        edge_apps = set(edge_location.apps)
        if edge_apps == self.apps_set:
            return
        cmd = RemoteCommand(edge_location.address)
        to_link = self.apps_set - edge_apps
        if to_link:
            for app in to_link:
                self.link_app(cmd, app)
        to_remove = edge_apps - self.apps_set
        if to_remove:
            for app in to_remove:
                self.remove_app(cmd, app)

    def monitor(self):
        self.logger.info('Using "%s" as applications dir' %(self.apps_dir))
        while True:
            try:
                self.get_apps()
                self.snapshot.memcache_load()
                for edge_location in self.snapshot.edge_locations:
                    self.check(edge_location)
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.logger.info('Exiting...')
                exit()
            except Exception as e:
                self.logger.exception(e)
                exit()


def setup_logging():
    logger = logging.getLogger('conf-monitor')
    logger.setLevel(logging.INFO)
    # create the file handler
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set the format of the log entries
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s',
                                  '%d-%b-%Y %H:%M:%S')
    console.setFormatter(formatter)
    logger.addHandler(console)

def main():
    argParser = OptionParser(description='Configuration monitor for CDS')
    argParser.add_option('--appsdir', dest='appsdir', type=str,
                         default='apps/',
                         help='directory where the application configuration'
                         ' files are being stored')
    (options, args) = argParser.parse_args()
    setup_logging()
    cmon = ConfMonitor(options.appsdir)
    cmon.monitor()

if __name__ == '__main__':
    main()
