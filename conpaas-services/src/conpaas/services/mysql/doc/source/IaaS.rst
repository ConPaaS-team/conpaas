====
IaaS
====
Core for opearations with open nebula. 

.. py:class:: OneXmlrpcNode()

   .. py:method:: __init__(self, node):

      Sets parameters from input parameter node.

      .. py:attribute:: id

         Id of service node.

      .. py:attribute:: state

         State of service node.

      .. py:attribute:: name

         Name of service node.

      .. py:attribute:: template

         Template of service node.

      .. py:attribute:: public_ip

         Ip of service node.

      :param node: Information about node.

.. py:class:: OneXmlrpc(NodeDriver)

   XMLRPC driver for OpenNebula.

   .. py:method:: __init__(self, uname, password, scheme, host, port):

      Uses input parameters for connection to OpenNebula

      :param uname: Username used when connecting to OpenNebula.
      :param password: Password used when connecting to OpenNebula.
      :param scheme: Scheme used when connecting to OpenNebula.
      :param host: Host used when connecting to OpenNebula.
      :param port: Port used when connecting to OpenNebula.

   .. py:method:: list_nodes(self):

      :rtype: Returns dictionary of all nodes. 

   .. py:method:: create_node(self, **kwargs):

      Using inpute parameters determines which template to use and which id to use for image and network. 

      :param kwargs: Determines which template will be used and with what parameters. 
      :rtype: returns response of allocating new service node. 

   .. py:method:: destroy_node(self, id):

      Removes service node idenfied by parameter id

      :param id: Id of service node that will be removed.

   .. py:method:: list_sizes(self, location=None)

      Returns different NodeSize. Atm does not have usefull function.

      :param location:
      :rtype: Returns information about 3 different Node sizes. 

.. py:class:: IaaSClient

   .. py:attribute:: NodeStates:

      In the begining states are defined

   .. code-block:: python

    RUNNING = NodeState.RUNNING
    REBOOTING = NodeState.REBOOTING
    TERMINATED = NodeState.TERMINATED
    PENDING = NodeState.PENDING
    UNKNOWN = NodeState.UNKNOWN

   .. py:method:: __config_opennebula_xmlrpc(self, iaas_config)

      Sets scheme, host, port, path, username, password, img_id, on_ex_network_id one_context_manager_script, one_context_agent_script and driver according to values in iaas_config file.

      .. py:attribute:: scheme 

         Scheme that will be used when connectiong to OpenNebula.

      .. py:attribute:: host

         Host that will be used when connecting to OpenNebula.

      .. py:attribute:: port

         Port that will be used when connecting to OpenNebula.

      .. py:attribute:: path

         Path that will be used when connecting to OpenNebula.

      .. py:attribute:: username

         Username that will be used when connecting to OpenNebula.

      .. py:attribute:: password

         Password that will be used when connecting to OpenNebula.

      .. py:attribute:: img_id

         Id of image on OpenNebula that will be used when creating new service node.

      .. py:attribute:: on_ex_network_id

         Id of network on OpenNebula that will be used when creating new service node.

      .. py:attribute:: one_context_manager_script

         Path to manager script that will be used in template.

      .. py:attribute:: one_context_agent_script

         Path to agent script that will be used in template.

      .. py:attribute:: driver

         Calls :py:meth:`OneXmlrpc`.

      :param iaas_config: Configuration file containing everything needed for connecting to OpenNebula.

   .. py:method:: __config_opennebula(self, iaas_config)

      .. py:attribute:: scheme

      .. py:attribute:: hostname

      .. py:attribute:: port

      .. py:attribute:: path

      .. py:attribute:: username

      .. py:attribute:: password

      .. py:attribute:: img_id

      .. py:attribute:: size_id

      .. py:attribute:: on_ex_network_id

      .. py:attribute:: on_ex_network_gateawy

      .. py:attribute:: driver

      :param iaas_config:

   .. py:method:: __config_ec2(self, iaas_config)

      .. py:attribute:: username

      .. py:attribute:: password

      .. py:attribute:: ec2_ex_securitygroup

      .. py:attribute:: ec2_ex_keyname

      .. py:attribute:: img_id

      .. py:attribute:: size_id 

      .. py:attribute:: driver

      :param iaas_config:

   .. py:method:: __setdriver(self, iaas_config)

      Raises Exception if iaas_config doesnt have name of driver. Calls appropriate method according to driver name. If drivername is OPENNEBULA :py:meth:`__config_opennebula` is called. If drivername is OPENNEBULA_XMLRPC :py:meth:`__config_opennebula_xmlrpc` is called and if drivername is EC2 :py:meth:`__config_ec2` is called

      :param iaas_config: Configuration file containing everything needed for connecting to OpenNebula.

   .. py:method:: __init__(self, iaas_config)

      Calls :py:meth:`__setdriver` with iaas_config as a parameter.

      :param iaas_config: Configuration file containing everything needed for connecting to OpenNebula.

   .. py:method:: listVMs(self)

      Constructs dictionary with information about all service nodes.

      :rtype: Returns information about all service nodes. 

   .. py:method:: getVMInfo(self, vm_id)

      Gets information about service node identified by vm_id.

      :param vm_id: Used to identifie service node
      :rtype: Returns information about service node.

   .. py:method:: newInstance(self, function)

      Creates new service node using appropriate driver. Returns id, state, name and ip of created service ndoe.

      :param function: Function of service node. Manager or agent.
      :rtype: Returns information about service node.

   .. py:method:: killInstance(self, vm_id)

      Deletes service node using appropriate driver. 
     
      :param vm_id: Id of service node that will be deleted. 
      :rtype: if service node is not found returns False

.. py:attribute:: logger

   Used for logging information.
