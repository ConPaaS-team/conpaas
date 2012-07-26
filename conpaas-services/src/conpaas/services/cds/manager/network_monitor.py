#!/usr/bin/python

import logging
from optparse import OptionParser
import select
import socket
import time

from edge import EdgeLocation, NetworkSnapshot
from map import GlobalMap


class NetworkMonitor:

    def __init__(self, port, map_filename):
        self.port = port
        self.map_filename = map_filename
        self.logger = logging.getLogger('network-monitor')
        self.cmap = GlobalMap(map_filename)
        self.logger.info('Loaded %d countries from "%s"'
                         %(len(self.cmap.map), map_filename))
        self.cmap.check_connectivity()
        self.logger.info('The graph of countries is connected...')

    def read_and_close(self, sock, edge_locations):
        try:
            data = sock.recv(4096)
            edge_location = EdgeLocation.from_text(data)
            if not edge_location in edge_locations:
                edge_locations.append(edge_location)
            else:
                self.logger.info('Edge location %s already part of the snapshot'
                                 % (edge_location))
        except Exception as e:
            self.logger.exception(e)
            addr = str(sock.getpeername())
            self.logger.error('Mishandling subscribe from %s: "%s"'
                              %(addr, data))
        finally:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

    def monitor(self):
        prev_snapshot = NetworkSnapshot()
        snapshot = NetworkSnapshot()
        last_snapshot = time.time()
        exceptionCount = 0
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self.port))
        sock.listen(0)
        self.logger.info('Listening on port %d' %(self.port))
        readFds = set([sock])
        while True:
            try:
                timeout = last_snapshot + snapshot.interval - time.time()
                rs, ws, xs = select.select(readFds, [], [], timeout)
                exceptionCount = 0
                if not rs:
                    # timeout, so we take a snapshot with what we got
                    if snapshot != prev_snapshot:
                        self.logger.info('Taking snapshot with %s'
                                         %(str(snapshot)))
                    self.cmap.assign_edge_locations(snapshot.edge_locations)
                    self.cmap.update_memcache()
                    snapshot.memcache_save()
                    last_snapshot = time.time()
                    prev_snapshot.edge_locations = snapshot.edge_locations
                    snapshot.clear()
                    continue
                for readFd in rs:
                    if readFd == sock:
                        # incoming connection
                        conn, addr = sock.accept()
                        readFds.add(conn)
                    else:
                        self.read_and_close(readFd, snapshot.edge_locations)
                        readFds.remove(readFd)
            except KeyboardInterrupt:
                self.logger.info('Exiting...')
                sock.close()
                exit()
            except select.error as e:
                self.logger.exception(e)
                # this might happen if we miss a deadline with other operations
                if timeout < 0:
                    last_snapshot += snapshot.interval
                exceptionCount += 1
                # if we get more than 3 exceptions in a row, we give up
                if exceptionCount > 3:
                    sock.close()
                    exit()


def setup_logging():
    logger = logging.getLogger('network-monitor')
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
    argParser = OptionParser(description='Network monitor for CDS')
    argParser.add_option('--map', dest='map', type=str,
                         default='globalmap.txt',
                         help='the file containing the graph of countries')
    argParser.add_option('--port', dest='port', type=int, default=7777,
                         help='the port to listen for network snapshot'
                         ' subscribers')
    (options, args) = argParser.parse_args()
    setup_logging()
    nmon = NetworkMonitor(options.port, options.map)
    nmon.monitor()

if __name__ == '__main__':
    main()
