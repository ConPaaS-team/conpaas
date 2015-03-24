import sys
import os

from cps.base import BaseClient

class Client(BaseClient):

    def info(self, app_id, service_id):
        service = BaseClient.info(self, app_id, service_id)
        
        nodes = self.callmanager(app_id, service['sid'], "list_nodes", False, {})
        if 'master' in nodes and nodes['master']:
            # Only one master
            master = nodes['master'][0]
            params = { 'serviceNodeId': master }
            details = self.callmanager(app_id, service['sid'], "get_node_info", False, params)
            print "master:", details['serviceNode']['ip']

        if 'node' in nodes:
            # Multiple nodes
            for node in nodes['node']:
                params = { 'serviceNodeId': node }
                details = self.callmanager(app_id, service['sid'], "get_node_info", False, params)
                print "node:", details['serviceNode']['ip']

    def usage(self, aid, sid ):
        BaseClient.usage(self, aid, sid)
        print ""
        print "    ----Service specific commands-------"
        print ""
        print "    add_nodes         appid serviceid count"
        print "    remove_nodes      appid serviceid count"
        print "    upload_code       appid serviceid filename  # upload a new code version"
        print "    list_uploads      appid serviceid           # list uploaded code versions"
        print "    download_code     appid serviceid version   # download a specific code version"
        print "    enable_code       appid serviceid version   # set a specific code version active"
        print "    delete_code       appid serviceid version   # delete a specific code version"
        print "    run               appid serviceid           # deploy the application"

    def main(self, argv):
        command = argv[1]
   
        if command in ( 'add_nodes', 'remove_nodes', 'upload_code', 'list_uploads',
                        'download_code', 'enable_code', 'delete_code', 'run' ):
            try:                                                      
                aid = int(argv[2])
                sid = int(argv[3])                             
            except (IndexError, ValueError):                          
                self.usage(0,0)                                   
                sys.exit(0)                                           
                                                              
            self.check_service_id(aid, sid)                              

  
        if command in ( 'add_nodes', 'remove_nodes'):
            try:
                count = int(argv[4])
            except (IndexError, ValueError):
                self.usage(0,0)
                sys.exit(0)

            # call the method
            res = self.callmanager(aid, sid, command, True, { 'count': count })
            if 'error' in res:
                print res['error']
            else:
                print "Service", sid, "is performing the requested operation (%s)" % command

        if command == 'upload_code':
            try: 
                filename = argv[4]
                if not (os.path.isfile(filename) and os.access(filename, os.R_OK)):
                    raise IndexError                                               
            except IndexError:                                                     
                self.usage(0,0)                                                
                sys.exit(0)                                                        
                                                                       
            getattr(self, command)(aid, sid, filename)                    
        
        if command == 'run':            
            getattr(self, command)(aid, sid)                    
    
        if command == 'list_uploads':                                                              
            res = self.callmanager(aid, sid, 'list_code_versions', False, {})                           
                                                                                           
            def add_cur(row):                                                                      
                if 'current' in row:                                                               
            	    row['current'] = '      *'                                                     
        	else:                                                                              
                    row['current'] = ''                                                            
                return row                                                                         
                                                                                           
            data = [ add_cur(el) for el in res['codeVersions'] ]                                   
            print self.prettytable(( 'current', 'codeVersionId', 'filename', 'description' ), data)
        
        if command in ( 'enable_code', 'download_code', 'delete_code' ):
            try:                                         
                code_version = argv[4]                   
            except IndexError:                           
                self.usage(0,0)                      
                sys.exit(0)                              
                                                 
            getattr(self, command)(aid, sid, code_version)    


    def upload_code(self, app_id, service_id, filename):
        contents = open(filename).read()

        files = [ ( 'code', filename, contents ) ]

        res = self.callmanager(app_id, service_id, "/", True, { 'method': "upload_code_version", }, files)
        if 'error' in res:
            print res['error']
        else:
            print "Code version %(codeVersionId)s uploaded" % res


    def download_code(self, app_id, service_id, version):
        res = self.callmanager(app_id, service_id, 'list_code_versions', False, {})

        if 'error' in res:
            print res['error']
            sys.exit(0)

        filenames = [ code['filename'] for code in res['codeVersions']
                if code['codeVersionId'] == version ]

        if not filenames:
            print "ERROR: Cannot download code: invalid version %s" % version
            sys.exit(0)

        destfile = filenames[0]

        params = { 'codeVersionId': version }
        res = self.callmanager(app_id, service_id, "download_code_version",
            False, params)

        if 'error' in res:
            print res['error']

        else:
            open(destfile, 'w').write(res)
            print destfile, 'written'


    def enable_code(self, app_id, service_id, code_version):
        params = { 'codeVersionId': code_version }

        res = self.callmanager(app_id, service_id, "enable_code", True, params)

        if 'error' in res:
            print res['error']

        else:
            print code_version, 'enabled'


    def delete_code(self, app_id, service_id, code_version):
        params = { 'codeVersionId': code_version }

        res = self.callmanager(app_id, service_id, "delete_code_version", True, params)

        if 'error' in res:
            print res['error']

        else:
            print code_version, 'deleted'


    def run(self, app_id, service_id):
        params = {}
        res = self.callmanager(app_id, service_id, "run", True, params)

        if 'error' in res:
            print res['error']
        else:
            print 'Service running'
