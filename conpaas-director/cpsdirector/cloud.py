import os.path
import simplejson

from netaddr import IPNetwork

from conpaas.core.controller import Controller
from conpaas.core.misc import file_get_contents
from conpaas.core.node import ServiceNode

from cpsdirector.x509cert import generate_certificate
from cpsdirector.common import config_parser, log
from cpsdirector.user import User
from cpsdirector import db

from flask import Blueprint
cloud_page = Blueprint('cloud_page', __name__)

class ManagerController(Controller):

    def __init__(self, service_name, service_id, user_id, cloud_name, app_id, vpn):
        self.config_parser = self.__get_config(str(service_id), str(user_id),
                                               str(app_id), service_name, vpn)

        Controller.__init__(self, self.config_parser)
        self.service_name = service_name
        self.service_id = service_id
        self.user_id = user_id
        self.cloud_name = cloud_name
        self.role = "manager"

    def _get_certificate(self, email, cn, org):
        user_id = self.config_parser.get("manager", "USER_ID")
        service_id = self.config_parser.get("manager", "SERVICE_ID")
        cert_dir = self.config_parser.get('conpaas', 'CERT_DIR')

        return generate_certificate(cert_dir, user_id, service_id,
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
        try:
            tmpl_values['cloud_script'] = file_get_contents(
                os.path.join(cloud_scripts_dir, cloud))
        except IOError:
            tmpl_values['cloud_script'] = ''

        # Get manager setup file
        mngr_setup = file_get_contents(
            os.path.join(mngr_scripts_dir, 'manager-setup'))

        tmpl_values['mngr_setup'] = mngr_setup.replace('%DIRECTOR_URL%',
                                                       director)

        # Get cloud config values from director.cfg
        cloud_sections = ['iaas']
        if self.config_parser.has_option('iaas', 'OTHER_CLOUDS'):
            cloud_sections.extend(
                [cloud_name for cloud_name
                 in self.config_parser.get('iaas', 'OTHER_CLOUDS').split(',')
                 if self.config_parser.has_section(cloud_name)])

        def __extract_cloud_cfg(section_name):
            tmpl_values['cloud_cfg'] += "["+section_name+"]\n"
            for key, value in self.config_parser.items(section_name):
                tmpl_values['cloud_cfg'] += key.upper() + " = " + value + "\n"

        tmpl_values['cloud_cfg'] = ''
        for section_name in cloud_sections:
            __extract_cloud_cfg(section_name)

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

        mngr_cfg = mngr_cfg.replace('%CLOUD_NAME%', self.cloud_name);
        # mngr_cfg = mngr_cfg.replace('%CLOUD_TYPE%', cloud_type);
        cloud = self.get_cloud_by_name(self.cloud_name)

        # OpenNebula, EC2. etc
        mngr_cfg = mngr_cfg.replace('%CLOUD_TYPE%',
                self.config_parser.get(self.cloud_name, 'DRIVER'))  

        mngr_cfg = mngr_cfg.replace('%CLOUD_MACHINE_TYPE%',
                self.config_parser.get(self.cloud_name, 'INST_TYPE'))

        if self.config_parser.has_option(self.cloud_name, 'COST_PER_TIME'):
            mngr_cfg = mngr_cfg.replace('%CLOUD_COST_PER_TIME%',
                    self.config_parser.get(self.cloud_name, 'COST_PER_TIME'))

        if self.config_parser.has_option(self.cloud_name, 'MAX_VMS'):
            mngr_cfg = mngr_cfg.replace('%CLOUD_MAX_VMS%',
                    self.config_parser.get(self.cloud_name, 'MAX_VMS'))

        if self.config_parser.has_option('iaas', 'MAX_VMS_ALL_CLOUDS'):
            mngr_cfg = mngr_cfg.replace('%CLOUD_MAX_VMS_ALL_CLOUDS%',
                    self.config_parser.get('iaas', 'MAX_VMS_ALL_CLOUDS'))
        # mngr_cfg = mngr_cfg.replace('%CLOUD_COST_PER_TIME%', cloud_cost_per_time);

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

            if self.config_parser.has_option('conpaas', 'VPN_BOOTSTRAP_NODES'):
                mngr_cfg += '\nIPOP_BOOTSTRAP_NODES = %s' % self.config_parser.get(
                    'conpaas', 'VPN_BOOTSTRAP_NODES')

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
        uid = self.config_parser.get("manager", "USER_ID")
        service_id = self.config_parser.get("manager", "SERVICE_ID")

        user = User.query.filter_by(uid=uid).one()
        log('Decrement user %s credit: sid=%s, old_credit=%s, decrement=%s' % (
            uid, service_id, user.credit, value))
        user.credit -= value

        if user.credit > -1:
            db.session.commit()
            log('New credit for user %s: %s' % (uid, user.credit))
            return True

        db.session.rollback()
        return False

    def stop(self, vmid):
        log('Trying to stop service %s on cloud %s' % (vmid, self.cloud_name))
        cloud = self.get_cloud_by_name(self.cloud_name)

        if not cloud.connected:
            cloud._connect()

        cloud.kill_instance(ServiceNode(vmid, None, None, self.cloud_name))
        self._stop_reservation_timer()

    def get_cloud_by_name(self, cloud_name):
        return [ cloud for cloud in self.get_clouds() 
            if cloud.get_cloud_name() == cloud_name ][0]

    def __get_config(self, service_id, user_id, app_id, service_type="", vpn=None):
        """Add manager configuration"""
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


    def _stop_reservation_timer(self):
        for reservation_timer in self._Controller__reservation_map.values():
            reservation_timer.stop()


def start(service_name, service_id, user_id, cloud_name, app_id, vpn):
    """Start a manager for the given service_name, service_id and user_id,
       on cloud_name

    Return (node_ip, node_id, cloud_name)."""

    if (cloud_name == 'default'):
        cloud_name = 'iaas'

    # Create a new controller
    controller = ManagerController(service_name, service_id, user_id,
                                    cloud_name, app_id, vpn)

    cloud = controller.get_cloud_by_name(cloud_name)
    # Create a context file for the specific service
    controller.generate_context(service_name, cloud)

    # FIXME: test_manager(ip, port) not implemented yet. Just return True.
    node = controller.create_nodes(1, lambda ip, port: True, None, cloud)[0]

    controller._stop_reservation_timer()

    return node.ip, node.id, cloud.get_cloud_name()

@cloud_page.route("/available_clouds", methods=['GET'])
def available_clouds():
    """GET /available_clouds"""
    clouds = ['default']
    if config_parser.has_option('iaas','OTHER_CLOUDS'):
        clouds.extend([cloud_name for cloud_name
            in config_parser.get('iaas', 'OTHER_CLOUDS').split(',')
            if config_parser.has_section(cloud_name)])
    return simplejson.dumps(clouds)
