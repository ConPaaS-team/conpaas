import sys
import os

from cps.base import BaseClient

# TODO: as this file was created from a BLUEPRINT file,
# 	you may want to change ports, paths and/or methods (e.g. for hub)
#	to meet your specific service/server needs

class Client(BaseClient):

    def info(self, service_id, app_id):
        service = BaseClient.info(self, service_id, app_id)
        
        print "%s" % service

        # nodes = self.callmanager(app_id, service['sid'], "list_nodes", False, {})
        # if 'hub' in nodes and nodes['hub']:
        #     # Only one HUB
        #     hub = nodes['hub'][0]
        #     params = { 'serviceNodeId': hub }
        #     details = self.callmanager(app_id, service['sid'], "get_node_info", False, params)
        #     print "hub url: ", "http://%s:4444" % details['serviceNode']['ip']
        #     print "node url:", "http://%s:3306" % details['serviceNode']['ip']

        # if 'node' in nodes:
        #     # Multiple nodes
        #     for node in nodes['node']:
        #         params = { 'serviceNodeId': node }
        #         details = self.callmanager(app_id, service['sid'], "get_node_info", False, params)
        #         print "node url:", "http://%s:3306" % details['serviceNode']['ip']

    def usage(self, cmdname):
        BaseClient.usage(self, cmdname)
        print "    add_nodes         serviceid count"
        print "    remove_nodes      serviceid count"
        # print "    upload_code       serviceid filename  # upload a new code version"
        # print "    list_uploads      serviceid           # list uploaded code versions"
        # print "    enable_code       serviceid version   # set a specific code version active"
        print "    run               serviceid           # deploy the application"

    def main(self, argv):
        command = argv[1]
   
        # if command in ( 'add_nodes', 'remove_nodes', 'upload_code', 'list_uploads', 'enable_code', 'run' ): 
        if command in ( 'add_nodes', 'remove_nodes', 'run' ): 
            try:                                                      
                sid = int(argv[2])
                aid = int(argv[3])                                    
            except (IndexError, ValueError):                          
                self.usage(argv[0])                                   
                sys.exit(0)                                           
                                                              
            self.check_service_id(sid, aid)                                

  
        if command in ( 'add_nodes', 'remove_nodes'):
            try:
                count = int(argv[4])
            except (IndexError, ValueError):
                self.usage(argv[0])
                sys.exit(0)

            # call the method
            res = self.callmanager(aid, sid, command, True, { 'count': count })
            if 'error' in res:
                print res['error']
            else:
                print "Service", sid, "is performing the requested operation (%s)" % command

        # if command == 'upload_code':
        #     try: 
        #         filename = argv[4]
        #         if not (os.path.isfile(filename) and os.access(filename, os.R_OK)):
        #             raise IndexError                                               
        #     except IndexError:                                                     
        #         self.usage(argv[0])                                                
        #         sys.exit(0)                                                        
                                                                       
        #     getattr(self, command)(aid, sid, filename)                    
        
        if command == 'run':            
            getattr(self, command)(aid, sid)                    
    
        # if command == 'list_uploads':                                                              
        #     res = self.callmanager(aid, sid, 'list_code_versions', False, {})                           
                                                                                           
        #     def add_cur(row):                                                                      
        #         if 'current' in row:                                                               
        #     	    row['current'] = '      *'                                                     
        # 	else:                                                                              
        #             row['current'] = ''                                                            
        #         return row                                                                         
                                                                                           
        #     data = [ add_cur(el) for el in res['codeVersions'] ]                                   
        #     print self.prettytable(( 'current', 'codeVersionId', 'filename', 'description' ), data)
        
        # if command == 'enable_code':
        #     try:                                         
        #         code_version = argv[4]                   
        #     except IndexError:                           
        #         self.usage(argv[0])                      
        #         sys.exit(0)                              
                                                 
        #     getattr(self, command)(aid, sid, code_version)    


    
    def run(self,  app_id, service_id):
        params = {}
        res = self.callmanager( app_id, service_id, "run", True, params)

        if 'error' in res:
            print res['error']
        else:
            print 'Service running'
