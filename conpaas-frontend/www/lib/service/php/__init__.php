<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('logging');
require_module('service');
require_module('service/factory');
require_module('ui/instance/php');

class PHPService extends Service {

	protected $conf = null;
	protected $cds = null;

	public function __construct($data, $manager) {
		parent::__construct($data, $manager);
		if ($this->isCdnEnabled()) {
			$cds_data = ServiceData::getCdsByAddress($this->conf->cdn);
			$this->cds = ServiceFactory::create($cds_data);
		}
	}

	public function hasDedicatedManager() {
		return true;
	}

	public function getConfiguration() {
		if (!$this->isReachable()) {
			return null;
		}
		// It is needed to refresh the data
		//if ($this->conf !== null) {
		//	return $this->conf;
		//}
		$json = $this->managerRequest('get', 'get_configuration', array());
		$conf = json_decode($json);
		if ($conf == null) {
			return null;
		}
		$this->conf = $conf->result;
		return $this->conf;
	}

	public function getAppAddress() {
		$loadbalancer = $this->getNodeInfo($this->nodesLists['proxy'][0]);
		return $loadbalancer['ip'];
	}

	public function sendConfiguration($params) {
		return $this->managerRequest('post', 'update_php_configuration',
			$params);
	}

	public function createInstanceUI($node) {
		$info = $this->getNodeInfo($node);
		return new PHPInstance($info);
	}

	public function getInstanceRoles() {
		return array('proxy', 'web', 'backend');
	}

	public function requestShutdown() {
		// if we have cds enabled, we need to unsubscribe from it because once
		// the service is stopped the origin address will be lost
		if ($this->cds) {
			$this->cdnEnable(false, '');
			$this->cds->unsubscribe($this->getAppAddress());
		}
		// regular shutdown
		return parent::requestShutdown();
	}

	public function isCdnEnabled() {
		$conf = $this->getConfiguration();
		if ($conf && isset($conf->cdn) && $conf->cdn) {
			return true;
		}
		return false;
	}

	public function isAutoscalingON() {
		$conf = $this->getConfiguration();
		if ($conf && isset($conf->autoscaling) && $conf->autoscaling) {
			return true;
		}
		return false;
	}
	
	public function getCds() {
		return $this->cds;
	}

	public function cdnEnable($enable, $address) {
		return $this->managerRequest('post', 'cdn_enable',
			array('enable' => $enable, 'address' => $address));
	}

	public function getAvailableCds($uid) {
		$services_data = ServiceData::getAvailableCds($uid);
		$services = array();
		foreach ($services_data as $service_data) {
			$services []= ServiceFactory::create($service_data);
		}
		return $services;
	}
}

?>
