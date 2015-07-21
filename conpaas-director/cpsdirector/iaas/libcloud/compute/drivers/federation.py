# Federation Driver for LibCloud
# author marco.distefano@isti.cnr.it
import urlparse
import xml.etree.ElementTree as ET 
from xml.dom import minidom
from base64 import b64encode
import hashlib
import json
import sys, os
import re
from libcloud.utils.py3 import httplib
from libcloud.utils.py3 import next
from libcloud.utils.py3 import b

from libcloud.compute.base import NodeState, NodeDriver, Node, NodeLocation
from libcloud.common.base import Connection, ConnectionUserAndKey, JsonResponse, XmlResponse
from libcloud.compute.base import NodeImage, NodeSize
from libcloud.common.types import InvalidCredsError
from libcloud.compute.providers import Provider, get_driver


class ErrorNode(Node):
    def __init__(self):
        return super.__init__(-1,'error', 'error')

class EntryPoint(object):
    BASE_URL = '/federation-api'

    'USERS operations'
    USERS_URL='/users'

    'APPLICATIONS operations'
    APPLICATIONS_URL='/applications'

    OVFS_URL = '/ovfs'

    PROVIDERS_URL = '/providers'

    def SLATS_FEDERATION(self):
        return self.BASE_URL + "/federation/slats"

    'providers url'
    def PROVIDERS(self):
        return self.BASE_URL + self.PROVIDERS_URL

    'specific provider with <id> url'
    def PROVIDER_ID(self, id):
        return self.BASE_URL + self.PROVIDERS_URL + "/" + id

    'ovfs url'    
    def OVFS(self):
	return self.BASE_URL + self.OVFS_URL

    'specific ovf with <id> url'
    def OVF_ID(self, id):
        return self.BASE_URL + self.OVFS_URL + "/" + id 	

    'ovfs of the speific user'
    def USER_OVFS(self, id):
        return self.USER_ID(id) + self.OVFS_URL

    'users url'
    def USERS(self):
        return self.BASE_URL + self.USERS_URL

    'specific user with <id> url'
    def USER_ID(self, id):
        return self.BASE_URL + self.USERS_URL + "/" + id

    'specific slat url of user with <id>'
    def USER_ID_SLATS(self, id):
        return self.BASE_URL + self.USERS_URL + "/" + id + "/slats"

    'applications of the speific user'
    def USER_APPLICATIONS(self, id):
        return self.USER_ID(id) + self.APPLICATIONS_URL

    'application of the speific user'
    def USER_APPLICATION(self, id, app_id):
        return self.USER_APPLICATIONS(id) + "/" + app_id

class OVFResponse(XmlResponse):
    def success(self):
        return self.status == 200

class FedResponse(JsonResponse):

    def success(self):
        """
        Check if response has the appropriate HTTP response code to be a
        success.

        @rtype:  C{bool}
        @return: True is success, else False.
        """
        i = int(self.status)
        return i >= 200 and i <= 299

    def parse_error(self):
        """
        Check if response contains any errors.

        @raise: L{InvalidCredsError}

        @rtype:  C{ElementTree}
        @return: Contents of HTTP response body.
        """
        if int(self.status) == httplib.UNAUTHORIZED:
            raise InvalidCredsError(self.body)
	elif int(self.status) == 404:
	    return "Resource Not Found"
	elif int(self.status) == 500:
	    return "Internal Server Error"
        return self.body

class FedConnection(ConnectionUserAndKey):

    responseCls =  FedResponse

    def __init__(self, *args, **kwargs):
	super(FedConnection, self).__init__(*args, **kwargs)

    def add_default_headers(self, headers):
        headers["Accept"] = 'application/json'
        headers["X-Username"] = 'admin'
        return headers

class FederationNodeDriver(NodeDriver):

    ###########################
    # Federation node driver  #
    ###########################

    entry = EntryPoint()
    fedHost = 'localhost'
    fedPort = '8080'
    secure = True
    connectionCls = FedConnection
    name = 'Federation'
    type = Provider.FEDERATION
    config={}
    applicationOvfSmall = {'name':'', 'url': '', 'content': ''}
    applicationOvfMedium = {'name':'','url': '', 'content': ''}
    applicationOvfLarge = {'name':'','url': '', 'content': ''}
    applicationSLATSmall = {'name':'','url': '', 'content': ''}
    applicationSLATMedium = {'name':'','url': '', 'content': ''}
    applicationSLATLarge = {'name':'','url': '', 'content': ''}
    userUuid= ''
    userId= ''
    federationProviderUuid= ''
    federationProviderId= ''
    init = True
    slatsPath = os.path.dirname(os.path.abspath(__file__)) + '/../../slats/'

    def __init__(self, *args, **kwargs):
	
	print os.path.dirname(os.path.abspath(__file__))
	print "[Conpaas Contrail Federation Driver] \n"
	print "[Conpaas Contrail Federation Driver] Reading configuration properties ...\n"
	# Read the configuration files
        
	try:
		execfile(os.path.dirname(os.path.abspath(__file__))+"/../../conf/federationDriver.conf", self.config)
		# Setting the Federation Endpoint from config file
        	self.fedHost = self.config["federationHost"]
		self.fedPort = self.config["federationPort"]
		print " - host uri: http://" + self.fedHost + ":" + self.fedPort
		# Setting secure flag
		self.secure = self.config["federationSecureFlag"]

		# here we instatiate the https connection

		# retrieve the Ids and Uuids of the ConpaasUser and FederationProvider
		self.userUuid = self.config["userUuid"]
		print " - userUuid: " + self.userUuid
		self.userId = self.config["userId"]
		print " - userId: " + self.userId
		self.federationProviderUuid = self.config["federationProviderUuid"]
		print " - federationProviderUuid: " + self.federationProviderUuid
		self.federationProviderId = self.config["federationProviderId"]
		print " - federationProviderId: " + self.federationProviderId
		if self.userUuid == "":
			print "NO CONPAAS USER ON FEDERATION : ERROR"
			exit(0)
	except :
		print "ERROR: Configuration file corrupted"
		exit(0)       

	super(FederationNodeDriver, self).__init__(secure=self.secure, host=self.fedHost, port=self.fedPort, *args, **kwargs)
	print "setting driver start..."
    	self.initializeDriver()
	print "setting driver end."

    def initializeDriver(self):
	print "[Conpaas Contrail Federation Driver] Initialize Dirver\n"
	ovfSLAPrefixName = "Contrail"
	self.applicationOvfSmall['name'] = ovfSLAPrefixName + "OvfSmall"
	self.applicationOvfMedium['name'] = ovfSLAPrefixName + "OvfMedium"
	self.applicationOvfLarge['name'] = ovfSLAPrefixName + "OvfLarge"
	self.applicationSLATSmall['name'] = ovfSLAPrefixName + "SLATSmall"
	self.applicationSLATMedium['name'] = ovfSLAPrefixName + "SLATMedium"
	self.applicationSLATLarge['name'] = ovfSLAPrefixName + "SLATLarge"
	checkRegistration = {'small': False, 'medium': False, 'large': False}
	# check if SLATs is already registered
	
	slatsInfoReturn = self.user_slats_list()
	for slatItem in slatsInfoReturn:
		if slatItem["name"] == self.applicationSLATSmall['name']:
			self.applicationSLATSmall['url'] = slatItem["uri"]
			print " - SLATemplate Conpaas_SlaTSmall already registered: " + self.applicationSLATSmall['url'] +"\n"
			slatInfo = self.slat_info(EntryPoint.BASE_URL+self.applicationSLATSmall['url'])
			self.applicationSLATSmall['content'] = slatInfo['content']
			self.applicationOvfSmall['url'] = slatInfo["userOvfUri"]
			checkRegistration['small'] = True
		elif slatItem["name"] == self.applicationSLATMedium['name']:
			self.applicationSLATMedium['url'] = slatItem["uri"]
			print " - SLATemplate Conpaas_SlaTMedium already registered: " + self.applicationSLATMedium['url'] +"\n"
			slatInfo = self.slat_info(EntryPoint.BASE_URL+self.applicationSLATMedium['url'])
			self.applicationSLATMedium['content'] = slatInfo['content']
			self.applicationOvfMedium['url'] = slatInfo["userOvfUri"]
			checkRegistration['medium'] = True
		elif slatItem["name"] == self.applicationSLATLarge['name']:
			self.applicationSLATLarge['url'] = slatItem["uri"]
			print " - SLATemplate Conpaas_SlaTLarge already registered: " + self.applicationSLATLarge['url'] +"\n"
			slatInfo = self.slat_info(EntryPoint.BASE_URL+self.applicationSLATLarge['url'])
			self.applicationSLATLarge['content'] = slatInfo['content']
			self.applicationOvfLarge['url'] = slatInfo["userOvfUri"]
			checkRegistration['large'] = True

        if not checkRegistration['small']:
		# register ovf and slatemplate small
		self.applicationSLATSmall['content'] = self.xmlToString(self.slatsPath + self.config["slatsURI"][0])
		slatSmallReg = self.slat_registration(self.applicationSLATSmall['name'],"/url", self.applicationSLATSmall['content'])
		self.applicationSLATSmall['url'] = slatSmallReg
		slatInfo = self.slat_info(EntryPoint.BASE_URL+slatSmallReg)
		self.applicationOvfSmall['url'] = slatInfo["userOvfUri"]

	if not checkRegistration['medium']:
		# register ovf and slatemplate medium
		self.applicationSLATMedium['content'] = self.xmlToString(self.slatsPath + self.config["slatsURI"][1])
		slatMediumReg = self.slat_registration(self.applicationSLATMedium['name'],"/url", self.applicationSLATMedium['content'])
		self.applicationSLATMedium['url'] = slatMediumReg
		slatInfo = self.slat_info(EntryPoint.BASE_URL+slatMediumReg)
		self.applicationOvfMedium['url'] = slatInfo["userOvfUri"]

	if not checkRegistration['large']:
		# register ovf and slatemplate large
		self.applicationSLATLarge['content'] = self.xmlToString(self.slatsPath + self.config["slatsURI"][2])
		slatLargeReg = self.slat_registration(self.applicationSLATLarge['name'],"/url", self.applicationSLATLarge['content'])
		self.applicationSLATLarge['url'] = slatLargeReg
		slatInfo = self.slat_info(EntryPoint.BASE_URL+slatLargeReg)
		self.applicationOvfLarge['url'] = slatInfo["userOvfUri"]
	
	print " - OVFS and SLATs registered on Federation"
	print " - ovf small: " + self.applicationOvfSmall['url']
	print " - slat small: " + self.applicationSLATSmall['url']
	print " - ovf medium: " + self.applicationOvfMedium['url']
	print " - slat medium: " + self.applicationSLATMedium['url']
	print " - ovf large: " + self.applicationOvfLarge['url']
	print " - slat large: " + self.applicationSLATLarge['url']
    
    def slat_registration(self, name, slatUrl, slatContent):
        headers={}
        headers['Content-Type']='application/json'
	putUrl = EntryPoint.USER_ID_SLATS(self.entry, self.userUuid)
	slatBodyContent = {'name': name, 'url': '', 'content': slatContent}
	slatPutContent = json.dumps(slatBodyContent)
        returnPutSlat = self.connection.request(putUrl, data=slatPutContent, headers=headers, method='POST').object
	slatsInfoReturn = self.user_slats_list()
	for slaItem in slatsInfoReturn:
		if slaItem["name"] == name:
			slatUrl = slaItem["uri"]
	return  slatUrl

    def list_nodes(self):
        headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.USER_APPLICATIONS(self.entry, self.userUuid)
        nodelist = self.connection.request(url, headers=headers).object
	nodes = []
	for node in nodelist:
		appUuid = node["uri"].split('/')[4]
		nodes.append(self.node_info(appUuid))
        return nodes
   
    def create_node(self, appName, size):
	print "[Conpaas Contrail Federation Driver] Create Node\n"
        headers={}
        headers['Content-Type']='application/json'
	headers['Accept']='application/json'
	        
	url = EntryPoint.USER_APPLICATIONS(self.entry, self.userUuid)
	if size == 'small':
		applicationOvf = self.applicationOvfSmall['url']
		slaTemplateUrl = self.applicationSLATSmall['url']
	elif size == 'medium':
		applicationOvf = self.applicationOvfMedium['url']
		slaTemplateUrl = self.applicationSLATMedium['url']
	elif size == 'large':
		applicationOvf = self.applicationOvfLarge['url']
		slaTemplateUrl = self.applicationSLATLarge['url']
	else:
		print " - error: size of application unknown: size must be in {'small', 'medium', 'large'}"
		return

	appName = appName
        attributes = { 'userSLATemplateUrl': slaTemplateUrl }
	attributesJson = json.dumps(attributes)
        deployDesc = ''
	bodyContent = { 'name': appName,
                        'deploymentDesc': deployDesc,
                        'applicationOvf': applicationOvf,
                        'attributes': attributes}
	postAppBody = json.dumps(bodyContent)
	print "executing post..."
        create_app_resp = self.connection.request(url, headers=headers, data=postAppBody, method='POST')
	#retrive AppUuid created
	location = create_app_resp.headers['location']
	m = re.match(r".*/applications/([\w-]+)$", location)
	if m:
	    appUuid = m.group(1)
	print "application created with uuid: " + appUuid

	
	print "executing submit..."
	appUri = EntryPoint.USER_APPLICATION(self.entry, self.userUuid, appUuid) 
	self.submit_app(appUri)
	
	#retrieving offers and accept the first	
	appInfo = self.connection.request(appUri).object
	appAttributes = json.loads(appInfo["attributes"])
	negotiationId = appAttributes["negotiationIds"][0]
	getOffersUrl = EntryPoint.BASE_URL + slaTemplateUrl + '/negotiation/' + negotiationId + '/proposals'
	print getOffersUrl
	offers = self.connection.request(getOffersUrl)
	proposalId = offers.object[0]['proposalId']
	
	print "executing createAgreement..."
	body = {"appUuid":appUuid}
	createAgreementBody=json.dumps(body)
	createAgreementUrl = getOffersUrl +'/' + str(proposalId) + '/createAgreement'
	print createAgreementUrl
	createAgreementResp = self.connection.request(createAgreementUrl, headers=headers, data=createAgreementBody, method='POST')
	
	startAppUrl = appUri + '/start'
	print "executing start..."
	print startAppUrl
	startAppResp = self.connection.request(startAppUrl, method='PUT').object

        return self.node_info(appUuid)

    def submit_app(self, app_url):
	headers={}
        headers['Accept']='application/json'
	submitUrl = app_url + '/submit'
		
	print submitUrl
	body={}
	putBody=json.dumps(body)
	submit_app_resp = self.connection.request(submitUrl, headers=headers, method='PUT').object
	print submit_app_resp

    def node_info(self, appUuid):
        headers={}
	app_url = EntryPoint.USER_APPLICATION(self.entry, self.userUuid, appUuid)
        nodeinfo = self.connection.request(app_url, headers=headers).object
	networks = []
	for vmUri in nodeinfo["vms"]:
		urlVM = EntryPoint.BASE_URL + vmUri
		vminfo = self.connection.request(urlVM, headers=headers).object
		net = FederationNetwork(id=vminfo["VinNetId"], name=vminfo["NetAppName"], address=vminfo["vmVinAddress"], driver=self.connection.driver)	
		networks.append(net)
	
        return self._to_node(nodeinfo, networks)

    def destroy_node(self, node):
	app_id = node.id
	headers={}
	appUrl = EntryPoint.USER_APPLICATION(self.entry, self.userUuid, app_id)
        stopUrl = appUrl + '/stop'
	#try:
	stopAppResp = self.connection.request(stopUrl, headers=headers, method='PUT')
	if stopAppResp.status != 204:
    		print "stop application failed"
    		return False
	
	#except :
	#print "error in request" #+ stopAppResp.headers['content-type']
	killUrl = appUrl + '/kill'	
	killAppResp = self.connection.request(killUrl, headers=headers, method='PUT')
	if killAppResp.status != 204:
    		print "kill application failed"
    		return False
	return True

    def _to_node(self, node_data, networks):
        return  Node(id=node_data['uuid'],
                    name=node_data['name'],
                    state=node_data['state'],
		    public_ips=networks,
		    private_ips=[],
                    driver=self.connection.driver)


    def xmlToString(self, path):
	file = open(path,'r')
	#convert to string:
	data = file.read()
	#close file because we dont need it anymore:
	file.close()
	return data

    def user_slats_list(self):
	headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.USER_ID_SLATS(self.entry,self.userUuid)
        ovf_info = self.connection.request(url, headers=headers).object
        return ovf_info

    def slat_info(self, url):
        headers={}
        headers['Content-Type']='application/json'
        slatInfo = self.connection.request(url, headers=headers).object
        return slatInfo




class FederationNetwork(object):
    """
    You don't normally create a network object yourself; instead you use
    a driver and then have that create the network for you.

    >>> from libcloud.compute.drivers.dummy import DummyNodeDriver
    >>> driver = DummyNetworkDriver()
    >>> network = driver.create_network()
    >>> network = driver.list_networks()[0]
    >>> network.name
    'dummy-1'
    """

    def __init__(self, id, name, address, driver, extra=None):
        self.id = str(id)
        self.name = name
        self.address = address
        self.driver = driver
        self.extra = extra or {}

    def __repr__(self):
        return (('<FederationNetwork: name=%s, address=%s, '
                 'provider=%s ...>')
                % (self.name, self.address, self.driver.name))
