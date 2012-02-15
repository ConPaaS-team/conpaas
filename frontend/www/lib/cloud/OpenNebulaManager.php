<?php
/*
 * Copyright (C) 2010-2011 Contrail consortium.                                                                                                                       
 *
 * This file is part of ConPaaS, an integrated runtime environment                                                                                                    
 * for elastic cloud applications.                                                                                                                                    
 *                                                                                                                                                                    
 * ConPaaS is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by                                                                                               
 * the Free Software Foundation, either version 3 of the License, or                                                                                                  
 * (at your option) any later version.
 * ConPaaS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of                                                                                                     
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                                                                                      
 * GNU General Public License for more details.                                                                                                                       
 *
 * You should have received a copy of the GNU General Public License                                                                                                  
 * along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.
 */

require_module('logging');
require_module('db');

class OpenNebulaManager {
	
	protected $sid;
	protected $vmid;
	protected $user_data_file;
	private $instance_type;
	private $service_type;
	
	const CONF_FILENAME = 'opennebula.ini';

	public function __construct($data) {
		$this->service_type = $data['type'];
		$this->sid = $data['sid'];
		$this->vmid = $data['vmid'];
		$this->loadConfiguration();
	}
	
	protected function loadConfiguration($conf_filename=self::CONF_FILENAME) {
		$conf = parse_ini_file(Conf::CONF_DIR.'/'.$conf_filename, true);
		if ($conf === false) {
			throw new Exception('Could not read OpenNebula configuration file '
				.'opennebula.ini');
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
		$this->virtualization_type = $conf['virtualization_type'];
		$this->os_arch = $conf['os_arch'];
		$this->os_bootloader = $conf['os_bootloader'];
		$this->os_root = $conf['os_root'];
		$this->disk_target = $conf['disk_target'];
		$this->context_target = $conf['context_target'];
		
	}
	
	public function http_request($method, $resource, $xml=null) {
	  $ch = curl_init();
	  curl_setopt($ch, CURLOPT_URL, $this->opennebula_url.$resource);
	  curl_setopt($ch, CURLOPT_HEADER, 'Accept: */*');
	  curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC); 
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
	  if ($body === false) {
	  	dlog("Error sending cURL request to '".$this->opennebula_url.$resource.
	  		"': ".curl_error($ch));
	  }
	  return $body;
	}
	
	/**
	 * Instantiate a virtual image of the Manager.
	 * 
	 * @return string id of the virtual instance
	 * @throws Exception
	 */
	public function run() {
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
		
		/* This parameter is only needed for Xen */
		$bootloader_spec = '<BOOTLOADER>'.$this->os_bootloader.'</BOOTLOADER>';
		if (strcmp($this->virtualization_type, 'xen') != 0) {
			$bootloader_spec = '';
		}
		
		$response = $this->http_request('POST', '/compute',
		'<COMPUTE>'.
			'<NAME>conpaas</NAME>'.
			'<INSTANCE_TYPE>'. $this->instance_type .'</INSTANCE_TYPE>'.
			'<DISK>'.
				'<STORAGE href="'.$this->opennebula_url.'/storage/'.$this->image.'" />'.
				'<TARGET>'.$this->disk_target.'</TARGET>'.
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
				'<TARGET>'.$this->context_target.'</TARGET>'.
			'</CONTEXT>'.
		    '<OS>'.
				'<TYPE arch="'.$this->os_arch.'" />'.
				$bootloader_spec.
				'<ROOT>'.$this->os_root.'</ROOT>'.
			'</OS>'.
		'</COMPUTE>');
		if ($response === false) {
			throw new Exception('the OpenNebula instance was not created');
		}
		
		$obj = simplexml_load_string($response);
		if ($obj === false) {
			dlog('run(): Error response from OpenNebula: '.$response);
			throw new Exception('run(): Invalid response from opennebula');
		}
		/* get the instance id */
		return (string)$obj->ID;
	}
	
	public function resolveAddress($vmid) {
		$response = $this->http_request('GET', '/compute/'.$vmid);
		if ($response === false) {
			dlog('Failed to fetch state of node from OpenNebula: '.$response);
			return false;
		}
		
		$obj = simplexml_load_string($response);
		if ($obj === false) {
			dlog('getAddress(): Invalid response from opennebula: '.$response);
			return false;
		}
		/* get the instance id */
		if ( ((string)$obj->STATE) === 'ACTIVE' ) {
		    return (string)$obj->NIC->IP;
		}
		return false;
	}
	
	/**
	 * @return false if the state is not 'running'
	 * 		   the address (DNS) of the instance
	 * @throws Exception
	 */
	public function getAddress() {
		return $this->resolveAddress($this->vmid);
	}
	
	public function terminate() {
    	$response = $this->http_request('DELETE', '/compute/'.$this->vmid);
	}
}
?> 
