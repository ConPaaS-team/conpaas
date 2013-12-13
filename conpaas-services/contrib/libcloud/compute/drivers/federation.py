# Federation Driver for LibCloud
# author marco.distefano@isti.cnr.it
import urlparse

import xml.etree.ElementTree as ET 
from xml.dom import minidom
from base64 import b64encode
import hashlib
import json
import sys, os
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
	#elif int(self.status) == 404:
	#    return json.dumps({'STATUS' : '404', 'DESCRIPTION':'Resource not found'})
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
    ovfPath = os.path.dirname(os.path.abspath(__file__)) + '/../../ovfs/'

    def __init__(self, *args, **kwargs):
	
	print os.path.dirname(os.path.abspath(__file__))
	print "[Conpaas Contrail Federation Driver] \n"
	print "[Conpaas Contrail Federation Driver] Reading configuration properties ..\n"
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
	# check if Ovfs is already registered
	ovfSInfoReturn = self.user_ovf_list()
	for ovfItem in ovfSInfoReturn:
		if ovfItem["name"] == self.applicationOvfSmall['name']:
			self.applicationOvfSmall['url'] = ovfItem["uri"]
			print " - ovf Conpaas_OvfSmall already registered: " + self.applicationOvfSmall['url'] +"\n"
			ovfInfo = self.ovf_info(EntryPoint.BASE_URL+self.applicationOvfSmall['url'])
			self.applicationOvfSmall['content'] = ovfInfo['content']
			checkRegistration['small'] = True
		elif ovfItem["name"] == self.applicationOvfMedium['name']:
			self.applicationOvfMedium['url'] = ovfItem["uri"]
			print " - ovf Conpaas_OvfMedium already registered: " + self.applicationOvfMedium['url'] +"\n"
			ovfInfo = self.ovf_info(EntryPoint.BASE_URL+self.applicationOvfMedium['url']) 
			self.applicationOvfMedium['content'] = ovfInfo['content']
			checkRegistration['medium'] = True
		elif ovfItem["name"] == self.applicationOvfLarge['name']:
			self.applicationOvfLarge['url'] = ovfItem["uri"]
			print " - ovf Conpaas_OvfSmall already registered: " + self.applicationOvfLarge['url'] +"\n"
			ovfInfo = self.ovf_info(EntryPoint.BASE_URL+self.applicationOvfLarge['url'])
			self.applicationOvfLarge['content'] = ovfInfo['content']
			checkRegistration['large'] = True

	slatsInfoReturn = self.user_slats_list()
	for slatItem in slatsInfoReturn:
		if slatItem["name"] == self.applicationSLATSmall['name']:
			self.applicationSLATSmall['url'] = slatItem["uri"]
			print " - SLATemplate Conpaas_SlaTSmall already registered: " + self.applicationSLATSmall['url'] +"\n"
			slatInfo = self.slat_info(EntryPoint.BASE_URL+self.applicationSLATSmall['url'])
			self.applicationSLATSmall['content'] = slatInfo['content']
		elif slatItem["name"] == self.applicationSLATMedium['name']:
			self.applicationSLATMedium['url'] = slatItem["uri"]
			print " - SLATemplate Conpaas_SlaTMedium already registered: " + self.applicationSLATMedium['url'] +"\n"
			slatInfo = self.slat_info(EntryPoint.BASE_URL+self.applicationSLATMedium['url'])
			self.applicationSLATMedium['content'] = slatInfo['content']
		elif slatItem["name"] == self.applicationSLATLarge['name']:
			self.applicationSLATLarge['url'] = slatItem["uri"]
			print " - SLATemplate Conpaas_SlaTLarge already registered: " + self.applicationSLATLarge['url'] +"\n"
			slatInfo = self.slat_info(EntryPoint.BASE_URL+self.applicationSLATLarge['url'])
			self.applicationSLATLarge['content'] = slatInfo['content']

        if not checkRegistration['small']:
		# register ovf and slatemplate small
		self.applicationOvfSmall['content'] = self.xmlToString(self.ovfPath + self.config["ovfsURI"][0])
		smallOvfUrl=self.ovf_registration(self.applicationOvfSmall['name'],'small')
		self.applicationOvfSmall['url']= smallOvfUrl
		self.replaceOvfRefInSlat(self.ovfPath + self.config["slatsURI"][0], smallOvfUrl)
		self.applicationSLATSmall['content'] = self.xmlToString(self.ovfPath + self.config["slatsURI"][0])
		slatSmallReg = self.slat_registration(self.applicationSLATSmall['name'],"/url", self.applicationSLATSmall['content'])
		self.applicationSLATSmall['url'] = slatSmallReg

	if not checkRegistration['medium']:
		# register ovf and slatemplate medium
		self.applicationOvfMedium['content'] = self.xmlToString(self.ovfPath + self.config["ovfsURI"][1])
		mediumOvfUrl=self.ovf_registration(self.applicationOvfMedium['name'],'medium')	
		self.applicationOvfMedium['url']= mediumOvfUrl
		self.replaceOvfRefInSlat(self.ovfPath + self.config["slatsURI"][1], mediumOvfUrl)
		self.applicationSLATMedium['content'] = self.xmlToString(self.ovfPath + self.config["slatsURI"][1])
		slatMediumReg = self.slat_registration(self.applicationSLATMedium['name'],"/url", self.applicationSLATMedium['content'])
		self.applicationSLATMedium['url'] = slatMediumReg

	if not checkRegistration['large']:
		# register ovf and slatemplate large
		self.applicationOvfLarge['content'] = self.xmlToString(self.ovfPath + self.config["ovfsURI"][2])
		largeOvfUrl=self.ovf_registration(self.applicationOvfLarge['name'],'large')
		self.applicationOvfLarge['url']= largeOvfUrl
		self.replaceOvfRefInSlat(self.ovfPath + self.config["slatsURI"][2], largeOvfUrl)
		self.applicationSLATLarge['content'] = self.xmlToString(self.ovfPath + self.config["slatsURI"][2])
		slatLargeReg = self.slat_registration(self.applicationSLATLarge['name'],"/url", self.applicationSLATLarge['content'])
		self.applicationSLATLarge['url'] = slatLargeReg
	
	print " - OVFS and SLATs registered on Federation"
	print " - ovf small: " + self.applicationOvfSmall['url']
	print " - slat small: " + self.applicationSLATSmall['url']
	print " - ovf medium: " + self.applicationOvfMedium['url']
	print " - slat medium: " + self.applicationSLATMedium['url']
	print " - ovf large: " + self.applicationOvfLarge['url']
	print " - slat large: " + self.applicationSLATLarge['url']

    def replaceOvfRefInSlat(self, slatPath, ovfUrl):
	xmldoc = ET.parse(slatPath)
	root = xmldoc.getroot()
	entryChilds = root.findall('{http://www.slaatsoi.eu/slamodel}InterfaceDeclr/{http://www.slaatsoi.eu/slamodel}Properties/{http://www.slaatsoi.eu/slamodel}Entry/')
	i = 0	
	while i < len(entryChilds):
		if entryChilds[i].text == "OVF_URL":
			i = i + 1
			entryChilds[i].text = ovfUrl
			print entryChilds[i].text
		print i
		i = i + 1
	xmldoc.write(slatPath);

    def ovf_registration(self, name, size):
	headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.OVFS(self.entry)
	print url
	ovfContent = 'medium'
	if size == 'small':
		ovfContent = self.applicationOvfSmall['content']
	elif size == 'medium':
		ovfContent = self.applicationOvfMedium['content']
	elif size == 'large':
		ovfContent = self.applicationOvfLarge['content']
        bodyContent = {'name': name, 'providerId': self.federationProviderId, 'content': ovfContent}
	body = json.dumps(bodyContent)
        ovfReg = self.connection.request(url, data=body, headers=headers, method='POST').object
	ovfInfoReturn = self.ovf_list()
	for ovfItem in ovfInfoReturn:
		if ovfItem["name"] == name:
			ovfUri = ovfItem["uri"]
        bodyUserOvfContent = {'name': name, 'providerOvfId': ovfUri, 'content': ovfContent}
	userOvfBody = json.dumps(bodyUserOvfContent)
	userOvfUrl = EntryPoint.USER_OVFS(self.entry, self.userUuid)
	userOvfRet = self.connection.request(userOvfUrl, data=userOvfBody, headers=headers, method='POST').object
	userOvfGet = self.connection.request(userOvfUrl).object
        for userOvfItem in userOvfGet:
		if userOvfItem["name"] == name:
			userOvfUri = userOvfItem["uri"]
	return userOvfUri

    def slat_registration(self, name, slatUrl, slatContent):
        headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.SLATS_FEDERATION(self.entry) 
	bodyContent = {'name': name,'url': slatUrl}
        body = json.dumps(bodyContent)
        
	returnSlat = self.connection.request(url, data=body, headers=headers, method='POST').object
	fedslatUrl = ''
	getSlat = self.connection.request(url).object
	for slaItem in getSlat:
		if slaItem["name"] == name:
			fedslatUrl = slaItem["uri"]
	putUrl = EntryPoint.USER_ID_SLATS(self.entry, self.userUuid)
	slatBodyContent = {'name': name, 'url': fedslatUrl, 'content': slatContent}
	slatPutContent = json.dumps(slatBodyContent)
        returnPutSlat = self.connection.request(putUrl, data=slatPutContent, headers=headers, method='POST').object
	return  fedslatUrl

    def list_node(self, id):
        headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.USER_APPLICATIONS(self.entry, id)
        nodelist = self.connection.request(url, headers=headers).object
        return nodelist
   
    def create_node(self, appName, size):
	print "[Conpaas Contrail Federation Driver] Create Node\n"
        headers={}
        headers['Content-Type']='application/json'
	headers['Accept']='application/json'
	        
	url = EntryPoint.USER_APPLICATIONS(self.entry, self.userUuid)
	if size == 'small':
		applicationOvf = self.applicationOvfSmall['content']
		slaTemplateUrl = self.applicationSLATSmall['url']
	elif size == 'medium':
		applicationOvf = self.applicationOvfMedium['content']
		slaTemplateUrl = self.applicationSLATMedium['url']
	elif size == 'large':
		applicationOvf = self.applicationOvfLarge['content']
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
        create_app_resp = self.connection.request(url, headers=headers, data=postAppBody, method='POST').object
	url = EntryPoint.USER_APPLICATIONS(self.entry, self.userUuid)
        nodesinfo = self.connection.request(url).object
	print nodesinfo
	appUri = None;
	for node in nodesinfo:
		if node["name"] == appName:
			appUri = node["uri"]
	startAppUrl = EntryPoint.BASE_URL  + appUri + '/start'
	print startAppUrl

	startAppResp = self.connection.request(startAppUrl, method='PUT').object
	
	#app_id = create_app_resp.something for retrieve the app_id	
	
	
	#slaProposal = submit_app_resp.something for retrive the proposal(s)
	#startUrl = EntryPoint.USER_APPLICATION(self.entry, id, app_id) + '/start'
	#print startUrl
	#here we have to set the SLAProposal on content's request for conclude negotiation
	#submit_app_resp = self.connection.request(startUrl, headers=headers, method='PUT').object
	
	return startAppUrl
        #return submit_app_resp	

    def submit_app(self, app_id):
	headers={}
        headers['Accept']='application/json'
	submitUrl = EntryPoint.USER_APPLICATION(self.entry, self.userUuid, app_id) + '/submit'
	body={}
	putBody=json.dumps(body)
	submit_app_resp = self.connection.request(submitUrl, headers=headers, method='PUT').object

    def node_info(self, id, app_id):
        headers={}
        url = EntryPoint.USER_APPLICATION(self.entry, id, app_id)
        nodeinfo = self.connection.request(url, headers=headers).object
        vmInfoUrl=nodeinfo["vms"][0]
        urlVM=url+vmInfoUrl
        # How get information about VMs in applications?????

        # vmInfo = self.connection.request(urlVM, headers=headers).object
        # print vmInfo
        # return self._to_node(nodeinfo)
        return nodeinfo

    def only_init(self):
	return "execute init"

    def _to_node(self, node_data):
        return  Node(id=node_data['uuid'],
                    name=node_data['name'],
                    state=node_data['state'],
                    public_ips=node_data['ip_addresses'],
                    private_ips=[],
                    driver=self.connection.driver)


    def xmlToString(self, path):
	file = open(path,'r')
	#convert to string:
	data = file.read()
	#close file because we dont need it anymore:
	file.close()
	return data

    def ovf_list(self,):
        headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.OVFS(self.entry)
        ovf_info = self.connection.request(url, headers=headers).object
        return ovf_info

    def user_ovf_list(self):
        headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.USER_OVFS(self.entry,self.userUuid)
        ovf_info = self.connection.request(url, headers=headers).object
        return ovf_info


    def ovf_info(self, url):
        headers={}
        headers['Content-Type']='application/json'
        #url = EntryPoint.OVF_ID(self.entry, providerUuid)
        ovf_info = self.connection.request(url, headers=headers).object
        return ovf_info

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


    ####################################################################################################################################################################
    # The following methods were implemented for test purpose.
    # Not useful for Conpaas
    ####################################################################################################################################################################
    def list_fed_users(self):
        headers={}
	headers['Accept']='application/json'
        url = EntryPoint.USERS(self.entry)
	print url + "\n"
        users_list = self.connection.request(url, headers=headers).object
        return users_list

    def get_fed_id_user(self, id):
        headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.USER_ID(self.entry, id)
        user_info = self.connection.request(url, headers=headers).object
        return user_info

    def register_user(self, username, password, firstName, lastName, email):
        headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.USERS(self.entry)
        bodyContent = {'username': username, 'password': password, 'lastName': lastName, 'firstName': firstName, 'email': email}
        body = json.dumps(bodyContent)
        user_info = self.connection.request(url, data=body, method='POST').object
        return user_info


    def provider_registration(self, name, providerUri, typeId, attribute=None):
	headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.PROVIDERS(self.entry)
        bodyContent = {'name': name, 'providerUri': providerUri, 'typeId': typeId, 'attribute': attribute}
        body = json.dumps(bodyContent)
        prov_reg = self.connection.request(url, data=body, method='POST').object
        return prov_reg

    def provider_info(self, providerUuid):
        headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.PROVIDER_ID(self.entry, providersUuid)
        prov_info = self.connection.request(url, headers=headers).object
        return prov_info

    def providers_list(self):
        headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.PROVIDERS(self.entry)
        prov_list = self.connection.request(url, headers=headers).object
        return prov_list
   
    """ 
        DELETE doesn't work.
        It executes a simple GET.
 
    def delete_user(self, id):
        headers={}
        headers['Content-Type']='application/json'
        url = EntryPoint.USER_ID(self.entry, id)
        print url
        resp = self.connection.request(url, method='DELETE')
        return resp.status
    """
