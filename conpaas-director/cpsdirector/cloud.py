import os.path
import simplejson, copy
import StringIO
from netaddr import IPNetwork

# from conpaas.core.controller import Controller
from conpaas.core.misc import file_get_contents
from conpaas.core.node import ServiceNode

from cpsdirector.x509cert import generate_certificate
from cpsdirector.common import config_parser, log
from cpsdirector.user import User
from cpsdirector import db

from flask import Blueprint, request, g 
# from cpsdirector.iaas import iaas
from cpsdirector.iaas.controller import Controller, ManagerController, AgentController
# from cpsdirector.iaas.controller import Controller
from cpsdirector.user import cert_required
from ConfigParser import ConfigParser
from conpaas.core.node import ServiceNode
from cpsdirector.common import build_response




cloud_page = Blueprint('cloud_page', __name__)

class Resource(db.Model):
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vmid = db.Column(db.String(80), unique=True, nullable=False)
    app_id = db.Column(db.Integer, db.ForeignKey('application.aid'))
    ip = db.Column(db.String(80))
    role = db.Column(db.String(10))
    cloud = db.Column(db.String(20))
    application = db.relationship('Application', backref=db.backref('resource',
                                  lazy="dynamic"))

    def __init__(self, **kwargs):
        # Default values
        for key, val in kwargs.items():
            setattr(self, key, val)

    def to_dict(self):
        res = {}
        for c in self.__table__.columns:
            res[c.name] = getattr(self, c.name)
        res['app_name'] = self.application.name
        return res


    def remove(self):
        db.session.delete(self)
        db.session.commit()
        log('Resource %s removed properly' % self.rid)
        return True


def get_resource_by_id(vmid):
    res = Resource.query.filter_by(vmid=vmid).first()
    if not res:
        log('Resource %s does not exist' % vmid)
        return
    return res

@cloud_page.route("/available_clouds", methods=['GET'])
def available_clouds():
    """GET /available_clouds"""
    clouds = ['default']
    if config_parser.has_option('iaas','OTHER_CLOUDS'):
        clouds.extend([cloud_name for cloud_name
            in config_parser.get('iaas', 'OTHER_CLOUDS').split(',')
            if config_parser.has_section(cloud_name)])
    return simplejson.dumps(clouds)



def _create_nodes(kwargs):
    role = kwargs.pop('role')
    cloud_name = kwargs.pop('cloud_name')
    
    app_id = kwargs.pop('app_id')
    user_id = '%s'%g.user.uid
    nodes = None

    if role == 'manager':
        vpn = kwargs.pop('vpn')
        controller = ManagerController(user_id, app_id, vpn)
        controller.generate_context(cloud_name)      
        nodes = controller.create_nodes(1,  cloud_name)

    else:
        count = kwargs.pop('count')
        service_id = kwargs.pop('service_id')
        service_type = kwargs.pop('service_type')
        manager_ip = kwargs.pop('manager_ip')
        context = kwargs.pop('context')

        from cpsdirector.application import get_app_by_id
        application = get_app_by_id(user_id, app_id)
  
        controller = AgentController(user_id, app_id, service_id, service_type, manager_ip)
        controller.generate_context(cloud_name, context)
        
        nodes = controller.create_nodes(count, cloud_name)
    
    if nodes:
        for node in nodes:
            resource = Resource(vmid=node.vmid, ip=node.ip, app_id=app_id, role=role, cloud=cloud_name)
            db.session.add(resource)
    
        # flush() is needed to get auto-incremented rid
        db.session.flush()
        db.session.commit()
      
    return nodes



@cloud_page.route("/create_nodes", methods=['POST'])
@cert_required(role='manager')
def create_nodes():
    """GET /create_nodes"""
    
    app_id = request.values.get('app_id')
    service_id = request.values.get('service_id')
    service_type = request.values.get('service_type')
    manager_ip = request.values.get('manager_ip')
    # role = request.values.get('role')

    

    count = int(request.values.get('count'))
    cloud_name = request.values.get('cloud_name')
    context = simplejson.loads(request.values.get('context').replace("'", "\""))
    # inst_type = request.values.get('inst_type')
    nodes = _create_nodes({'role':'agent', 'app_id':app_id, 'cloud_name':cloud_name, 
                    'service_id':service_id, 'service_type':service_type, 'count':count, 
                    'manager_ip':manager_ip, 'context':context})
    
    # log('nodes string: %s' % simplejson.dumps([node.to_dict() for node in nodes]))
    return simplejson.dumps([node.to_dict() for node in nodes])



@cloud_page.route("/remove_nodes", methods=['POST'])
@cert_required(role='manager')
def remove_nodes():
    """GET /create_nodes"""
    nodes = simplejson.loads(request.values.get('nodes'))
    
    log('Deleting %s nodes' % len(nodes))
    serv_nodes = [ServiceNode(node['vmid'], node['ip'],node['private_ip'],node['cloud_name'],node['weight_backend']) for node in nodes]        
    controller = Controller()
    controller.setup_default()
    controller.delete_nodes(serv_nodes)

    for node in nodes:
        res = get_resource_by_id(node['vmid'])
        res.remove()

    return simplejson.dumps({})



@cloud_page.route("/list_resources", methods=['GET'])
@cert_required(role='user')
def list_resources():
    from cpsdirector.application import Application
    res = [res.to_dict() for res in Resource.query.join(Application).filter_by(user_id=g.user.uid)]
    
    return build_response(simplejson.dumps(res))
