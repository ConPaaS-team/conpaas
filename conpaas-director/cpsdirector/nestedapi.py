import ast

from flask import Blueprint
from flask import jsonify, request

from cpsdirector import db
from cpsdirector.user import User
from cpsdirector.common import log, config_parser
from cpsdirector.cloud import ManagerController
from cpsdirector.x509cert import generate_certificate

from conpaas.core.controller import Controller

from conpaas.core.node import ServiceNode
from conpaas.core import https
from flask import Blueprint
from flask import jsonify, request

from ConfigParser import ConfigParser

nestedapi_page = Blueprint('nestedapi_page', __name__)

controllers = {}

class AgentController(Controller):
    """ Controller used by the director for storing the information associated
        with each manager. It duplicates the certificate and credit deduction
        logic from ManagerController.    
    """
    
    def __init__(self, agent_config_parser):
        Controller.__init__(self, agent_config_parser)
        self.config_parser.set('manager', 'CERT_DIR', config_parser.get('conpaas', 'CERT_DIR'))
         
    def _generate_agent_certificate(self, email, cn, org):
        user_id = self.config_parser.get("manager", "USER_ID")
        service_id = self.config_parser.get("manager", "SERVICE_ID")
        cert_dir = self.config_parser.get('manager', 'CERT_DIR')

        return generate_certificate(cert_dir, user_id, service_id,
                                    "manager", email, cn, org)
        
    def _get_certificate(self):
        return self._generate_agent_certificate(email="info@conpaas.eu",
                                           cn="ConPaaS",
                                           org="Contrail")

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

@nestedapi_page.route("/nestedapi/update_configuration.php", methods=['POST'])
def update_configuration():
    global controllers
    cert = request.values['cert']
    service_type = request.values['service_name']
      
    d = ast.literal_eval(request.values['config'])
    d['manager']['conpaas_home'] = config_parser.get('conpaas', 'CONF_DIR')
    
    agent_config_parser = ConfigParser()

    for section in d:
        agent_config_parser.add_section(section)
        for option in d[section]:
            agent_config_parser.set(section, option, d[section][option])

    controller = AgentController(agent_config_parser)
    controller.generate_context(service_type)

    controllers[cert] = controller
    
    return jsonify({})    

@nestedapi_page.route("/nestedapi/create_node.php", methods=['POST'])
def create_node():
    #dictionary that holds for each manager its associated controller
    #TODO push the dictionary to a persistent structure
    global controllers

    cert = request.values['cert']
    cloud_name = request.values['cloud']

    controller = controllers[cert]

    if cloud_name == 'default':
            cloud_name = 'iaas'

    https.client.conpaas_init_ssl_ctx('/etc/cpsdirector/certs', 'director')
    
    #create the VM
    cloud = controller.get_cloud_by_name(cloud_name)
    node = controller.create_nodes(1, lambda ip, port: True, None, cloud)[0]
    
    #send to the manager information about the newly created node
    node_info = node.__dict__

    return jsonify({'result': node_info})

@nestedapi_page.route("/nestedapi/delete_node.php", methods=['POST'])
def delete_node():
    global controllers

    cert = request.values['cert']
    node_info = ast.literal_eval(request.values['node'])
    node = ServiceNode(node_info['id'], node_info['ip'],
                       node_info['private_ip'], node_info['cloud_name'],
                       node_info['weightBackend'])

    #delete node from the manager's controller (stopping reservation timers)
    if cert in controllers:
        controller = controllers[cert]
        controller.delete_nodes([node])

    return jsonify({'result': True})

def remove_controller(service_id):
    """Delete the controller corresponding to the manager associated with
    the service_id.
    """
    global controllers
    
    controller_cert = None    

    for cert in controllers:
        if int(controllers[cert].config_parser.get("manager", "SERVICE_ID")) == service_id:
            controller_cert = cert
            break

    if controller_cert:
        del controllers[controller_cert]
