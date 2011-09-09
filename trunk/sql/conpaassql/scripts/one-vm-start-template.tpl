NAME   = conpaassql-manager
CPU    = 0.2
MEMORY = 512
   OS     = [
   arch = "i686",
   boot = "hd",
   root     = "hda" ]
DISK   = [
   image_id = "80",
   bus = "scsi",
   readonly = "no" ]
NIC    = [ NETWORK_ID = 24 ]
GRAPHICS = [
  type="vnc"
  ]
CONTEXT = [
  target=sdc,
  files = /home/contrail/manager/conpaassql-install.sh
  ]