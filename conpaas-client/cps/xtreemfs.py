import sys

from cps.base import BaseClient

class Client(BaseClient):

    def info(self, service_id):
        service = BaseClient.info(self, service_id)

        print 'persistent:', service['persistent']
        print 'osd_volume_size:', service['osd_volume_size']

        nodes = self.callmanager(service['sid'], "list_nodes", False, {})
        if 'error' in nodes:
            return

        print nodes

        for role in ( 'dir', 'mrc', 'osd' ):
            print "\n", role.upper(), "nodes:"

            for node in nodes[role]:
                params = { 'serviceNodeId': node }
                details = self.callmanager(service['sid'], "get_node_info", False, params)

                if 'error' in details:
                    print node, details['error']
                    continue

                if role == 'dir':
                    port = 30638

                if role == 'osd':
                    port = 30640
                    
                if role == 'mrc':
                    port = 30636

                print "http://%s:%s" % (details['serviceNode']['ip'], port)

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print "    add_nodes         serviceid count [cloud] # add the specified number of osd nodes"
        print "    remove_nodes      serviceid count [cloud] # remove the specified number of osd nodes"
        print "    list_volumes      serviceid"
        print "    create_volume     serviceid vol_name"
        print "    delete_volume     serviceid vol_name"
        print "    list_policies     serviceid policy_type # [ osd_sel | replica_sel | replication ]"
        print "    set_policy        serviceid policy_type vol_name policy [factor]"
        print "    toggle_persistent serviceid"
        print "    set_osd_size      serviceid vol_size"
# TODO: add when there is more than one striping policy
#        print "    list_striping_policies     serviceid"
#        print "    set_striping_policy        serviceid vol_name policy width stripe-size"

    def main(self, argv):
        command = argv[1]

        if command in ( 'add_nodes', 'remove_nodes', 'list_volumes',
                'create_volume', 'delete_volume', 'list_policies',
                'set_policy', 'toggle_persistent', 'set_osd_size' ):
            try:
                sid = int(argv[2])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)
                
            self.check_service_id(sid)

        if command in ( 'add_nodes', 'remove_nodes' ):
            try:
                params = {
                    'osd': int(argv[3]),
                    #'dir': int(argv[4]),
                    #'mrc': int(argv[5])
                }
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            if len(argv) == 4:
                params['cloud'] = 'default'
            else:
                params['cloud'] = argv[4]
            # call the method
            res = self.callmanager(sid, command, True, params)
            if 'error' in res:
                print res['error']
            else:
                print "Service", sid, "is performing the requested operation (%s)" % command

        if command == 'create_volume':
            try:
                params = { 'volumeName': argv[3] }
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            res = self.callmanager(sid, 'createVolume', True, params)
            if 'error' in res:
                print res['error']
            else:
                print "Volume", params['volumeName'], "created" 

        if command == 'delete_volume':
            try:
                params = { 'volumeName': argv[3] }
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            res = self.callmanager(sid, 'deleteVolume', True, params)
            if 'error' in res:
                print res['error']
            else:
                print "Volume", params['volumeName'], "deleted" 

        if command == 'list_volumes':
            res = self.callmanager(sid, 'listVolumes', False, {})
            if 'error' in res:
                print res['error']
            else:
                print res['volumes']

        if command == 'list_policies':
            try:
                policy_type = argv[3] 
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            if policy_type == 'osd_sel':
                command = 'list_osd_sel_policies'

            elif policy_type == 'replica_sel':
                command = 'list_replica_sel_policies'

            elif policy_type == 'replication':
                command = 'list_replication_policies'

            else:
                self.usage(argv[0])
                sys.exit(0)

            res = self.callmanager(sid, command, False, {})
            if 'error' in res:
                print res['error']
            else:
                print res['policies']

        if command == 'set_policy':
            try:
                policy_type = argv[3] 
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            try:
                params = { 'volumeName': argv[4], 'policy': argv[5] }
            except IndexError:
                self.usage(argv[0])
                sys.exit(0)

            if policy_type == 'osd_sel':
                command = 'set_osd_sel_policy'

            elif policy_type == 'replica_sel':
                command = 'set_replica_sel_policy'

            elif policy_type == 'replication':
                command = 'set_replication_policy'
                try:
                    # set_replication_policy requires a 'factor'
                    params['factor'] = argv[6]
                except IndexError:
                    self.usage(argv[0])
                    sys.exit(0)
            else:
                self.usage(argv[0])
                sys.exit(0)

            res = self.callmanager(sid, command, True, params)
            if 'error' in res:
                print res['error']
            else:
                print res['stdout']
                print "Policy set." 

        if command == 'toggle_persistent':
            res = self.callmanager(sid, command, True, {})

            print "This service is now",

            if not res['persistent']:
                print "not",

            print "persistent"

        if command == 'set_osd_size':
            params = {}
            try:
                params['size'] = int(argv[3])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            res = self.callmanager(sid, command, True, params)
            print "OSD volume size is now %s MBs" % res['osd_volume_size']

#        if command in 'set_striping_policy':
#            try:
#                params = { 'volumeName': argv[3], 'policy': argv[4], 'width': argv[5], 'stripe-size': argv[6] }
#            except IndexError:
#                self.usage(argv[0])
#                sys.exit(0)
#
#            res = self.callmanager(sid, command, True, params)
#            if 'error' in res:
#                print res['error']
#            else:
#                print res['stdout']
#                print "Policy set." 

