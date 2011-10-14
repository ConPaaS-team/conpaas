<?php
  // Copyright (C) 2010-2011 Contrail consortium.
  //
  // This file is part of ConPaaS, an integrated runtime environment 
  // for elastic cloud applications.
  //
  // ConPaaS is free software: you can redistribute it and/or modify
  // it under the terms of the GNU General Public License as published by
  // the Free Software Foundation, either version 3 of the License, or
  // (at your option) any later version.
  //
  // ConPaaS is distributed in the hope that it will be useful,
  // but WITHOUT ANY WARRANTY; without even the implied warranty of
  // MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  // GNU General Public License for more details.
  //
  // You should have received a copy of the GNU General Public License
  // along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.

require_once('logging.php');
require_once('Service.php');
require_once('DB.php');
require_once('lib/aws-sdk/sdk.class.php');

class OpenNebula {
	
	protected $vmid;
	
	private $user_data_file;
	private $instance_type;
	private $service_type;
	
	public function __construct($data) {
		$this->service_type = $data['type'];
		$this->sid = $data['sid'];
		$this->vmid = $data['vmid'];
		$this->loadConfiguration();
	}
	
	private function loadConfiguration() {
		$conf = parse_ini_file(Conf::CONF_DIR.'/opennebula.ini', true);
		if ($conf === false) {
			throw new Exception('Could not read OpenNebula configuration file opennebula.ini');
		}
		$this->user_data_file = $conf['user_data_file'];
		$this->instance_type = $conf['instance_type'];
		$this->opennebula_url = $conf['url'];
		$this->user = $conf['user'];
		$this->passwd = $conf['passwd'];
		$this->image = $conf['image'];
		$this->network = $conf['network'];
		$this->gateway = $conf['gateway'];
		$this->nameserver = $conf['nameserver'];
	}
	
	public function http_request($method, $resource, $xml=null) {
	  $ch = curl_init();
	  curl_setopt($ch, CURLOPT_URL, $this->opennebula_url . $resource);
	  curl_setopt($ch, CURLOPT_HEADER, 'Accept: */*');
	  curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC ) ; 
      curl_setopt($ch, CURLOPT_USERPWD, $this->user.':'.sha1($this->passwd));
      switch($method) {
        case 'POST':
          curl_setopt($ch, CURLOPT_POST, 1);
	      curl_setopt($ch, CURLOPT_POSTFIELDS, $xml);
          break;
        case 'DELETE':
          curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'DELETE');
          break;
        default:
      }
	  curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
	  $body = curl_exec($ch);
	  return $body;
	}
	
	/**
	 * Instantiate a virtual image of the Manager.
	 * @return string id of the virtual instance
	 * @throws Exception
	 */
	public function createManagerInstance() {
		$user_data = file_get_contents($this->user_data_file);
		if ($user_data === false) {
			throw new Exception('could not read manager user data: '.
				$this->user_data_file);
		}
		$user_data = str_replace(
						array('%CONPAAS_SERVICE_TYPE%', '%CONPAAS_SERVICE_ID%'),
						array(strtoupper($this->service_type), $this->sid),
						$user_data);
		$hex_user_data = bin2hex($user_data);
		$response = $this->http_request('POST', '/compute',
		'<COMPUTE>'.
			'<NAME>conpaas</NAME>'.
			'<INSTANCE_TYPE>'. $this->instance_type .'</INSTANCE_TYPE>'.
			'<DISK>'.
				'<STORAGE href="'.$this->opennebula_url.'/storage/'.$this->image.'" />'.
			'</DISK>'.
			'<NIC>'.
				'<NETWORK href="'.$this->opennebula_url.'/network/'.$this->network.'" />'.
			'</NIC>'.
			'<CONTEXT>'.
				'<HOSTNAME>$NAME</HOSTNAME>'.
				'<IP_PUBLIC>$NIC[IP]</IP_PUBLIC>'.
				'<IP_GATEWAY>'.$this->gateway.'</IP_GATEWAY>'.
				'<NAMESERVER>'.$this->nameserver.'</NAMESERVER>'.
				'<USERDATA>'.$hex_user_data.'</USERDATA>'.
				'<TARGET>sdb</TARGET>'.
			'</CONTEXT>'.
		    '<OS><TYPE arch="x86_64" /></OS>'.
		'</COMPUTE>');
		dlog($response);
		if ($response === FALSE) {
			dlog($response);
			throw new Exception('the OpenNebula instance was not created');
		}
		
		$obj = simplexml_load_string($response);
		if ($obj === FALSE) {
		  throw new Exception('Invalid response from opennebula');
		}
		/* get the instance id */
		return (string)$obj->ID;
	}
	
	/**
	 * @return false if the state is not 'running'
	 * 		   the address (DNS) of the instance
	 * @throws Exception
	 */
	public function getManagerAddress() {
		$response = $this->http_request('GET', '/compute/'.$this->vmid);
		if ($response === FALSE) {
			dlog($response);
			throw new Exception('Faile to fetch state of node from OpenNebula');
		}
		
		$obj = simplexml_load_string($response);
		if ($obj === FALSE) {
		  throw new Exception('Invalid response from opennebula');
		}
		/* get the instance id */
		if ( ((string)$obj->STATE) === 'ACTIVE' ) {
		    return (string)$obj->NIC->IP;
		}
		else {
		  return FALSE;
		}
	}
	
	public function terminateService() {
    	$response = $this->http_request('DELETE', '/compute/'.$this->vmid);
	}
}
?>
