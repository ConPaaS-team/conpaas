<?php

require_once('Service.php');

class LocalService extends Service {
	
	public function __construct($service_data) {
		parent::__construct($service_data);
	}
	
	public function getManagerAddress() {
		return $this->manager;
	}
	
	public function checkManagerInstance() {
		return false;
	}
	
	public function needsPolling() {
		return false;
	}
}