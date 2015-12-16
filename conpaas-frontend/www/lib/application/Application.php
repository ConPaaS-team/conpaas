<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */


// require_module('cloud');
require_module('logging');
require_module('https');

class Application {

	protected $aid, $name, $user_id, $manager, $status, $vmid;


	private $errorMessage = null;

	public static function stateIsStable($remoteState) {
		return true;
	}

	public function __construct($data) {
		foreach ($data as $key => $value) {
			$this->$key = $value;
		}

		if (isset($this->manager))
			$this->manager = 'https://'. $this->manager;
	}

	public function getErrorMessage() {
		return $this->errorMessage;
	}

	public function needsPolling() {
		return false;
	}

	public function getAID() {
		return $this->aid;
	}

	public function getUID() {
		return $this->uid;
	}

	public function getName() {
		return $this->name;
	}

	public function getManager() {
		return $this->manager;
	}

	public function isManagerSet() {
		return isset($this->manager);
	}
	
	public function getVMID() {
		return $this->vmid;
	}

	public function getStatus() {
		return $this->status;
	}

	private function decodeResponse($json, $method) {
		$response = json_decode($json, true);
		if ($response == null) {
			if (strlen($json) > 256) {
				$json = substr($json, 0, 256).'...[TRIMMED]';
			}
			throw new Exception('Error parsing response for '.$method.': "'.$json.'"');
		}
		if (isset($response['error']) && $response['error'] !== null) {
			$message = $response['error'];
			if (is_array($response['error'])) {
				$message = $response['error']['message'];
			}
			throw new ManagerException('Remote error: '.$message);
		}
		return $response;
	}

	public function managerRequest($http_method, $method, $service_id, array $params, $ping=false) {
		if ($http_method == "upload"){
			$params['method'] = $method;
			$json = HTTPS::post($this->manager, $params);
		}else
			$json = HTTPS::jsonrpc($this->manager, $http_method, $method, $service_id, $params, $ping);
		$this->decodeResponse($json, $method);
		return $json;
	}

	public function toArray() {
		return array(
			'aid' => $this->aid,
			'name' => $this->name,
			'manager' => $this->manager,
			'vmid' => $this->vmid,
			'status' => $this->status,
		);
	}
}
