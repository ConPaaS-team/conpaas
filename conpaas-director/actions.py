"""
start(service_name, service_id)
stop(vmid)
"""

import os
import sys
import time

from conpaas.core.controller import Controller

import common

def __try_read_file(filename):
    try:
        return open(filename).read()
    except IOError:
        print "Cannot read contextualization script " + filename
        return ""

def __specific_or_default_filename(base, service, suffix, force_default=False):
    filename = os.path.join(base, service + suffix)

    if not force_default and os.path.isfile(filename):
        return filename

    return filename.replace(service, 'default')

def __get_context_file(config, cloud, service, service_id):
    root_dir = config.get('conpaas', 'ROOT_DIR')
    cloud_scripts_dir = os.path.join(root_dir, 'scripts', 'cloud')
    cloud_cfg_dir     = os.path.join(root_dir, 'config', 'cloud')
    mngr_cfg_dir      = os.path.join(root_dir, 'config', 'manager')
    mngr_scripts_dir  = os.path.join(root_dir, 'scripts', 'manager')

    cloud_script = __try_read_file(os.path.join(cloud_scripts_dir, cloud))

    download_url = config.get('director', 'DIRECTOR_URL')
    mngr_setup   = __try_read_file(os.path.join(mngr_scripts_dir, 
        "manager-setup"))
    mngr_setup   = mngr_setup.replace('%FRONTEND_URL%', download_url)
    mngr_setup   = mngr_setup.replace('%CLOUD%', cloud)

    cloud_cfg = __try_read_file(os.path.join(cloud_cfg_dir, cloud + '.cfg'))

    # The local director.cfg can override values
    cloud_cfg = cloud_cfg.replace("USER =", 
        "USER = %s" % config.get("iaas", 'USER'))
    cloud_cfg = cloud_cfg.replace("PASSWORD =", 
        "PASSWORD = %s" % config.get("iaas", 'PASSWORD'))
    cloud_cfg = cloud_cfg.replace("IMAGE_ID =", 
        "IMAGE_ID = %s" % config.get("iaas", 'IMAGE_ID'))

    if cloud == "ec2":
        cloud_cfg = cloud_cfg.replace("SECURITY_GROUP_NAME =", 
            "SECURITY_GROUP_NAME = %s" % config.get("iaas", 
                'SECURITY_GROUP_NAME'))
        cloud_cfg = cloud_cfg.replace("KEY_NAME =", 
            "KEY_NAME = %s" % config.get("iaas", 'KEY_NAME'))
    # TODO: elif cloud == "opennebula":

    # Start with the default config
    mngr_cfg_filename = __specific_or_default_filename(mngr_cfg_dir, 
        service, '-manager.cfg', force_default=True)
    mngr_cfg = __try_read_file(mngr_cfg_filename)

    # Append service specific config (if any)
    mngr_cfg_specific_filename = __specific_or_default_filename(mngr_cfg_dir, 
        service, '-manager.cfg')
    if mngr_cfg_specific_filename != mngr_cfg_filename:
        mngr_cfg += __try_read_file(mngr_cfg_specific_filename)

    mngr_cfg = mngr_cfg.replace('%FRONTEND_URL%', download_url)
    mngr_cfg = mngr_cfg.replace('%CONPAAS_SERVICE_ID%', str(service_id))
    mngr_cfg = mngr_cfg.replace('%CONPAAS_SERVICE_TYPE%', service)

    mngr_start_filename = __specific_or_default_filename(mngr_scripts_dir, 
        service, '-manager-start')
    mngr_start_script = __try_read_file(mngr_start_filename)

    return "%s\n\n%s\n\ncat <<EOF > $ROOT_DIR/config.cfg\n%s\n%s\nEOF\n\n%s\n" % (
        cloud_script, mngr_setup, cloud_cfg, mngr_cfg, mngr_start_script)

def __getcloud(service_name="php", service_id=1):
    config = common.config
    if not config.has_section("manager"):
        config.add_section("manager")

    config.set("manager", "FE_SERVICE_ID", str(service_id))
    config.set("manager", "FE_CREDIT_URL", config.get('director', 'DIRECTOR_URL') + "/credit")
    config.set("manager", "FE_TERMINATE_URL", config.get('director', 'DIRECTOR_URL') + "/terminate")

    controller = Controller(config)

    # Mess with private attributes 
    c = controller._Controller__default_cloud 
    context = __get_context_file(config, config.get("iaas", "DRIVER"), 
        service_name, service_id)
    c.set_context_template(context)

    # Otherwise it locks forever
    controller._Controller__reservation_map['manager'].stop()
    return c

def start(service_name, service_id):
    c = __getcloud(service_name, service_id)
    new_vm = c.new_instances(1)[0]

    try:
        new_vm_id = new_vm['id']
    except TypeError:
        new_vm_id = new_vm.id

    ip = ''
    while not ip:
        vms = c.list_vms()
        ip = vms[new_vm_id]['ip']
        time.sleep(1)

    return ip, new_vm_id

    #controller._Controller__deduct_credit = lambda x: True
    #controller.create_nodes(1, 'get_service_info', 80, "ec2")

def stop(vmid):
    c = __getcloud()
    c._connect()
    # kill_instance() takes an object with an id attribute on newer versions of
    # libcloud
    class Node: pass
    n = Node()
    n.id = vmid
    c.kill_instance(n)

    # kill_instance() takes a string object on older versions of libcloud
    vmids = [ vm for vm in c.list_vms().keys() ]

    if vmid in vmids:
        try:
            c.kill_instance(vmid)
        except Exception:
            pass

if __name__ == "__main__":
    try:
        from conpaas.core.mservices import services
        available_services = services.keys()
        if sys.argv[1] not in available_services:
            print sys.argv[1], "is not a known service %s" % available_services
        else:
            start(sys.argv[1], 1)
    except IndexError:
        print "Usage: %s servicename" % sys.argv[0]
