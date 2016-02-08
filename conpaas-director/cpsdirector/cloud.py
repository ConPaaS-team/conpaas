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
from datetime import datetime

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
    service_id = db.Column(db.Integer, db.ForeignKey('service.sid'))
    charged = db.Column(db.Integer)
    ip = db.Column(db.String(80))
    role = db.Column(db.String(10))
    cloud = db.Column(db.String(20))
    created = db.Column(db.DateTime) 
    application = db.relationship('Application', backref=db.backref('resource', lazy="dynamic"))

    def __init__(self, **kwargs):
        # Default values
        for key, val in kwargs.items():
            setattr(self, key, val)
        self.charged = 0
        self.created = datetime.now()

    def to_dict(self):
        res = {}
        for c in self.__table__.columns:
            res[c.name] = getattr(self, c.name)
        res['app_name'] = self.application.name
        res['created'] = str(res['created'])
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


def _get_cloud_list(nodes_info):
    # the default cloud is always called 'iaas'
    for ninfo in nodes_info:
        if not ninfo['cloud'] or ninfo['cloud'] == 'default' or ninfo['cloud'] == 'None':
            ninfo['cloud'] = 'iaas'

    return list(set([ninfo['cloud'] for ninfo in nodes_info]))


from cpsdirector.credits import Credit
def _create_nodes(kwargs):

    role = kwargs.pop('role')
    nodes_info = kwargs.pop('nodes_info')
    clouds = _get_cloud_list(nodes_info)

    app_id = kwargs.pop('app_id')
    user_id = kwargs.pop('user_id')
    nodes = None
    service_id = 0

    from cpsdirector.application import Application, get_app_by_id
    application = get_app_by_id(user_id, app_id)
    if role == 'manager':
        vpn = kwargs.pop('vpn')
        controller = ManagerController(user_id, app_id, vpn)
        controller.generate_context(clouds)
        nodes = controller.create_nodes(nodes_info, clouds)

        application.status = Application.A_RUNNING
    else:
        service_id = kwargs.pop('service_id')
        service_type = kwargs.pop('service_type')
        manager_ip = kwargs.pop('manager_ip')
        context = kwargs.pop('context')
        startup_script = kwargs.pop('startup_script')

        log('type: %s' % service_type)

        controller = AgentController(user_id, app_id, service_id, service_type, manager_ip)
        controller.generate_context(clouds, context, startup_script)
        nodes = controller.create_nodes(nodes_info, clouds)

    if nodes:
        for node in nodes:
            resource = Resource(vmid=node.vmid, ip=node.ip, app_id=app_id, service_id=service_id, role=role, cloud=node.cloud_name)
            db.session.add(resource)

        db.session.flush()
        db.session.commit()

        Credit().check_credits()

    return nodes



@cloud_page.route("/create_nodes", methods=['POST'])
@cert_required(role='manager')
def create_nodes():
    """GET /create_nodes"""

    app_id = request.values.get('app_id')
    service_id = request.values.get('service_id')
    service_type = request.values.get('service_type')
    manager_ip = request.values.get('manager_ip')
    startup_script = request.values.get('startup_script', None)
    # role = request.values.get('role')

    # log('startup_script :%s' % startup_script)
    # FIXME: make this get driectly a json
    nodes_info = simplejson.loads(request.values.get('nodes_info').replace("u'", '"').replace("'", '"'))
    context = simplejson.loads(request.values.get('context').replace("'", "\""))
    # inst_type = request.values.get('inst_type')

    if g.user.credit <= 0:
        return simplejson.dumps({ 'error': True,'msg': 'Insufficient credits' })

    nodes = _create_nodes({ 'role':'agent', 'app_id':app_id, 'user_id':'%s'%g.user.uid,
                    'service_id':service_id, 'service_type':service_type, 'nodes_info':nodes_info, 
                    'manager_ip':manager_ip, 'context':context, 'startup_script':startup_script })

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



@cloud_page.route("/create_volume", methods=['POST'])
@cert_required(role='manager')
def create_volume():
    """GET /create_nodes"""

    size = int(request.values.get('size'))
    name = str(request.values.get('name'))
    vm_id =str(request.values.get('vm_id'))
    cloud = str(request.values.get('cloud'))

    controller = Controller()
    controller.setup_default()
    volume  = controller.create_volume(size, name, vm_id, cloud)

    log('Created volume %s ' % volume.id)
    
    return simplejson.dumps({'volume_id':volume.id })


@cloud_page.route("/attach_volume", methods=['POST'])
@cert_required(role='manager')
def attach_volume():
    """POST /attach_volume"""
    
    vm_id =str(request.values.get('vm_id'))
    volume_id = str(request.values.get('volume_id'))
    device_name = str(request.values.get('device_name'))
    cloud = str(request.values.get('cloud'))
    
    controller = Controller()
    controller.setup_default()
    controller.attach_volume(vm_id, volume_id, device_name, cloud)

    log('Attached volume %s to vm %s (cloud: %s)' % (volume_id, vm_id, cloud))
    
    return simplejson.dumps({})


@cloud_page.route("/detach_volume", methods=['POST'])
@cert_required(role='manager')
def detach_volume():
    """POST /detach_volume"""

    volume_id = str(request.values.get('volume_id'))
    cloud = str(request.values.get('cloud'))
    
    controller = Controller()
    controller.setup_default()
    controller.detach_volume(volume_id, cloud)

    log('Detached volume %s (cloud: %s)' % (volume_id, cloud))
    
    return simplejson.dumps({})

@cloud_page.route("/destroy_volume", methods=['POST'])
@cert_required(role='manager')
def destroy_volume():
    """POST /destroy_volume"""

    volume_id = str(request.values.get('volume_id'))
    cloud = str(request.values.get('cloud'))
    
    controller = Controller()
    controller.setup_default()
    controller.destroy_volume(volume_id, cloud)

    log('Destroyed volume %s (cloud: %s)' % (volume_id, cloud))
    
    return simplejson.dumps({})


# putting this in the user_page wasn't working for some non-obvious reason
@cloud_page.route("/credit", methods=['POST'])
@cert_required(role='manager')
def credit():
    log('manager is asking for credits')
    return simplejson.dumps({'credit': g.user.credit})


@cloud_page.route("/list_resources", methods=['GET'])
@cert_required(role='user')
def list_resources():
    from cpsdirector.application import Application
    res = [res.to_dict() for res in Resource.query.join(Application).filter_by(user_id=g.user.uid)]
    
    return build_response(simplejson.dumps(res))

