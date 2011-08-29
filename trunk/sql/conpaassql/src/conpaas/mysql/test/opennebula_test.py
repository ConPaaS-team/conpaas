'''
Created on Jul 28, 2011

@author: ales
'''
#from conpaas.iaas import IaaSClient
import oca

def xmlRPCtest():
    client = oca.Client('oneadmin:oneadmin', 'http://172.16.120.228:2633/RPC2')
    #new_host_id = oca.Host.allocate(client, 'host_name', 'im_xen', 'vmm_xen', 'tm_nfs')
    hostpool = oca.HostPool(client)    
    hostpool.info()
    for i in hostpool:
        print "Active host:"        
        print i.name, i.str_state
    vm_pool=oca.VirtualMachinePool(client)
    vm_pool.info(-2)
    print "All VMs:"        
    for i in vm_pool:
        print i.name, i.str_state    
    print "Allocating new VM..."
    #oca.VirtualMachine.
    rez=oca.VirtualMachine.allocate(client, '''NAME   = conpaassql01
CPU    = 0.2
MEMORY = 512
   OS     = [
   arch = "i686",
   boot = "hd",
   root     = "hda" ]
DISK   = [
   image = "Ubu10-10-rmq-3",
   bus = "scsi",
   readonly = "no" ]
NIC    = [ NETWORK = "Private LAN" ]
GRAPHICS = [
  type="vnc"
  ]
''')
    print rez

def xmlRPCtest2():
    client = oca.Client('oneadmin:oneadmin', 'http://172.16.120.228:2633/RPC2')
    rez=oca.VirtualMachinePool(client)
    rez.info(-2)
    vm = rez.get_by_id(424)
    
    #rez=oca.VirtualMachine.info(client, 424)
    print rez

if __name__ == '__main__':
    #xmlRPCtest()
    xmlRPCtest2()
    #CP = ConfigParser()
    #ONDriver = get_driver(Provider.OPENNEBULA)
    #driver = OpenNebulaNodeDriver("oneadmin", "oneadmin", False , "172.16.120.228", 4566)
    #driver.list_images()    
    #driver.list_nodes()
    #driver.list_locations()
    #CP.readfp(open("scripts/opennebula.conf"))
    #client = IaaSClient(CP)
    #print client.listVMs()
