from threading import Thread

from conpaas.core.expose import expose
from conpaas.core.manager import BaseManager

from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse

from conpaas.services.helloworld.agent import client

from conpaas.core.misc import check_arguments, is_in_list, is_not_in_list,\
    is_list, is_non_empty_list, is_list_dict, is_list_dict2, is_string,\
    is_int, is_pos_nul_int, is_pos_int, is_dict, is_dict2, is_bool,\
    is_uploaded_file

class HelloWorldManager(BaseManager):

    def __init__(self, config_parser, **kwargs):
        BaseManager.__init__(self, config_parser)
        self.state = self.S_INIT

    def get_service_type(self):
        return 'helloworld'

    def get_context_replacement(self):
        return dict(STRING='helloworld')

    def on_start(self, nodes):
        return self.on_new_nodes(nodes)

    def on_stop(self):
        self.logger.info("Removing nodes: %s" %[ node.id for node in self.nodes ])
        return self.nodes[:]

    def on_add_nodes(self, nodes):
        return self.on_new_nodes(nodes)

    def on_remove_nodes(self, node_roles):
        count = sum(node_roles.values())
        del_nodes = []
        cp_nodes = self.nodes[:]
        for _ in range(0, count):
            node = cp_nodes.pop()
            del_nodes += [ node ]
        if not cp_nodes:
            self.state = self.S_STOPPED
        else:
            self.state = self.S_RUNNING

        self.logger.info("Removing nodes: %s" %[ node.id for node in del_nodes ])
        return del_nodes

    def on_new_nodes(self, nodes):
        try:
            for node in nodes:
                client.startup(node.ip, self.AGENT_PORT)
            return True
        except Exception, err:
            self.logger.exception('_do_startup: Failed to create node: %s' % err)
            return False

    @expose('GET')
    def list_nodes(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        try:
            self.check_state([self.S_RUNNING, self.S_ADAPTING])
        except:
            return HttpJsonResponse({})

        return HttpJsonResponse({
              'helloworld': [ node.id for node in self.nodes ],
              })

    @expose('GET')
    def get_service_info(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        return HttpJsonResponse({'state': self.state_get(), 'type': 'helloworld'})

    @expose('GET')
    def get_node_info(self, kwargs):
        node_ids = [ str(node.id) for node in self.nodes ]
        exp_params = [('serviceNodeId', is_in_list(node_ids))]
        try:
            serviceNodeId = check_arguments(exp_params, kwargs)
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        for node in self.nodes:
            if serviceNodeId == node.id:
                serviceNode = node
                break

        return HttpJsonResponse({
            'serviceNode': {
                            'id': serviceNode.id,
                            'ip': serviceNode.ip,
                            'vmid': serviceNode.vmid,
                            'cloud': serviceNode.cloud_name
                            }
            })

    @expose('GET')
    def get_helloworld(self, kwargs):
        try:
            exp_params = []
            check_arguments(exp_params, kwargs)
            self.check_state([self.S_RUNNING])
        except Exception as ex:
            return HttpErrorResponse("%s" % ex)

        messages = []

        # Just get_helloworld from all the agents
        for node in self.nodes:
            data = client.get_helloworld(node.ip, self.AGENT_PORT)
            message = 'Received %s from %s' % (data['result'], node.id)
            self.logger.info(message)
            messages.append(message)

        return HttpJsonResponse({ 'helloworld': "\n".join(messages) })
