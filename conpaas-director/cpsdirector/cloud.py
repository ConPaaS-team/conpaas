import os.path

from netaddr import IPNetwork

from conpaas.core.controller import Controller
from conpaas.core.misc import file_get_contents

from cpsdirector import x509cert
from cpsdirector import common

class ManagerController(Controller):

    def __init__(self, config_parser, **kwargs):
        Controller.__init__(self, config_parser, **kwargs)
        self.role = "manager"

    def _get_certificate(self, email, cn, org):
        user_id = self.config_parser.get("manager", "USER_ID")
        service_id = self.config_parser.get("manager", "SERVICE_ID")
        cert_dir = self.config_parser.get('conpaas', 'CERT_DIR')

        return x509cert.generate_certificate(cert_dir, user_id, service_id,
                                             "manager", email, cn, org)

    def _get_context_file(self, service_name, cloud):
        """Override default _get_context_file. Here we generate the context
        file for managers rather than for agents."""
        conpaas_home = self.config_parser.get('conpaas', 'CONF_DIR')

        cloud_scripts_dir = os.path.join(conpaas_home, 'scripts', 'cloud')
        mngr_scripts_dir = os.path.join(conpaas_home, 'scripts', 'manager')
        mngr_cfg_dir = os.path.join(conpaas_home, 'config', 'manager')

        director = self.config_parser.get('director', 'DIRECTOR_URL')

        # Values to be passed to the context file template
        tmpl_values = {}

        # Get contextualization script for the cloud
        tmpl_values['cloud_script'] = file_get_contents(
            os.path.join(cloud_scripts_dir, cloud))

        # Get manager setup file
        mngr_setup = file_get_contents(
            os.path.join(mngr_scripts_dir, 'manager-setup'))

        tmpl_values['mngr_setup'] = mngr_setup.replace('%DIRECTOR_URL%',
                                                       director)

        # Get cloud config values from director.cfg
        tmpl_values['cloud_cfg'] = "[iaas]\n"
        for key, value in self.config_parser.items("iaas"):
            tmpl_values['cloud_cfg'] += key.upper() + " = " + value + "\n"

        # Get manager config file
        mngr_cfg = file_get_contents(
            os.path.join(mngr_cfg_dir, 'default-manager.cfg'))

        # Add service-specific config file (if any)
        mngr_service_cfg = os.path.join(mngr_cfg_dir,
                                        service_name + '-manager.cfg')

        if os.path.isfile(mngr_service_cfg):
            mngr_cfg += file_get_contents(mngr_service_cfg)

        # Modify manager config file setting the required variables
        mngr_cfg = mngr_cfg.replace('%DIRECTOR_URL%', director)
        mngr_cfg = mngr_cfg.replace('%CONPAAS_SERVICE_TYPE%', service_name)

        for option_name in 'SERVICE_ID', 'USER_ID', 'APP_ID':
            mngr_cfg = mngr_cfg.replace('%CONPAAS_' + option_name + '%',
                                        self.config_parser.get("manager",
                                                               option_name))

        # Check if we want to use IPOP. If so, add IPOP directives to manager
        # config file
        if self.config_parser.has_option('manager', 'IPOP_SUBNET'):
            ipop_subnet = self.config_parser.get('manager', 'IPOP_SUBNET')
            mngr_cfg += '\nIPOP_SUBNET = %s' % ipop_subnet

            ipop_network = IPNetwork(ipop_subnet).iter_hosts()

            # Skip the first IP address. IPOP uses it for internal purposes
            ipop_network.next()

            mngr_cfg += '\nIPOP_IP_ADDRESS = %s' % ipop_network.next()

            mngr_cfg += '\nIPOP_BASE_IP = %s' % self.config_parser.get(
                'conpaas', 'VPN_BASE_NETWORK')

            mngr_cfg += '\nIPOP_NETMASK = %s' % self.config_parser.get(
                'conpaas', 'VPN_NETMASK')

        tmpl_values['mngr_cfg'] = mngr_cfg

        # Add default manager startup script
        tmpl_values['mngr_start_script'] = file_get_contents(
            os.path.join(mngr_scripts_dir, 'default-manager-start'))

        # Or the service-specific one (if any)
        mngr_startup_scriptname = os.path.join(
            mngr_scripts_dir, service_name + '-manager-start')

        if os.path.isfile(mngr_startup_scriptname):
            tmpl_values['mngr_start_script'] = file_get_contents(
                mngr_startup_scriptname)

        # Get key and a certificate from CA
        mngr_certs = self._get_certificate(email="info@conpaas.eu",
                                           cn="ConPaaS",
                                           org="Contrail")

        tmpl_values['mngr_certs_cert'] = mngr_certs['cert']
        tmpl_values['mngr_certs_key'] = mngr_certs['key']
        tmpl_values['mngr_certs_ca_cert'] = mngr_certs['ca_cert']

        # Concatenate the files
        return """%(cloud_script)s

cat <<EOF > /tmp/cert.pem
%(mngr_certs_cert)s
EOF

cat <<EOF > /tmp/key.pem
%(mngr_certs_key)s
EOF

cat <<EOF > /tmp/ca_cert.pem
%(mngr_certs_ca_cert)s
EOF

%(mngr_setup)s

cat <<EOF > $ROOT_DIR/config.cfg
%(cloud_cfg)s
%(mngr_cfg)s
EOF

%(mngr_start_script)s""" % tmpl_values

    def deduct_credit(self, value):
        import cpsdirector

        uid = self.config_parser.get("manager", "USER_ID")

        user = cpsdirector.User.query.filter_by(uid=uid).one()
        user.credit -= value

        if user.credit > -1:
            cpsdirector.db.session.commit()
            return True

        cpsdirector.db.session.rollback()
        return False


def __get_config(service_id, user_id, app_id, service_type="", vpn=None):
    """Add manager configuration"""
    config_parser = common.config_parser

    if not config_parser.has_section("manager"):
        config_parser.add_section("manager")

    config_parser.set("manager", "SERVICE_ID", service_id)
    config_parser.set("manager", "USER_ID", user_id)
    config_parser.set("manager", "APP_ID", app_id)
    config_parser.set("manager", "CREDIT_URL",
                      config_parser.get('director',
                                        'DIRECTOR_URL') + "/credit")
    config_parser.set("manager", "TERMINATE_URL",
                      config_parser.get('director',
                                        'DIRECTOR_URL') + "/terminate")
    config_parser.set("manager", "CA_URL",
                      config_parser.get('director',
                                        'DIRECTOR_URL') + "/ca")

    config_parser.set("manager", "TYPE", service_type)

    if vpn:
        config_parser.set("manager", "IPOP_SUBNET", vpn)

    return config_parser


def __stop_reservation_timer(controller):
    for reservation_timer in controller._Controller__reservation_map.values():
        reservation_timer.stop()


def start(service_name, service_id, user_id, app_id, vpn):
    """Start a manager for the given service_name, service_id and user_id.

    Return (node_ip, node_id, cloud_name)."""
    config_parser = __get_config(str(service_id), str(user_id), str(app_id), service_name, vpn)
    # Create a new controller
    controller = ManagerController(config_parser)
    # Create a context file for the specific service
    controller.generate_context(service_name)

    # FIXME: test_manager(ip, port) not implemented yet. Just return True.
    node = controller.create_nodes(1, lambda ip, port: True, None)[0]

    # Stop the reservation timer or the call will not return
    __stop_reservation_timer(controller)

    return node.ip, node.id, config_parser.get('iaas', 'DRIVER')


def stop(vmid):
    config_parser = __get_config(vmid, "", "")
    # Create a new controller
    controller = ManagerController(config_parser)

    cloud = controller._Controller__default_cloud
    cloud._connect()

    class Node:
        pass
    n = Node()
    n.id = vmid
    cloud.kill_instance(n)

    __stop_reservation_timer(controller)
