<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('logging');
require_module('db');

class OpenNebulaManager extends Manager {

	protected $virtualization_type;
	protected $os_arch;
	protected $os_bootloader;
	protected $os_root;
	protected $disk_target;
	protected $context_target;

	const CONF_FILENAME = 'opennebula.ini';

	public function __construct($data) {
		parent::__construct($data);
		$this->loadConfiguration();
	}

	protected function loadConfiguration($conf_filename=self::CONF_FILENAME) {
		$conf = parse_ini_file(Conf::CONF_DIR.'/'.$conf_filename, true);
		if ($conf === false) {
			throw new Exception('Could not read OpenNebula configuration file '
				.'opennebula.ini');
		}
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
		$user_data = $this->createContextFile('opennebula');
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

	public function terminate() {
    	$response = $this->http_request('DELETE', '/compute/'.$this->vmid);
	}
}
?>
