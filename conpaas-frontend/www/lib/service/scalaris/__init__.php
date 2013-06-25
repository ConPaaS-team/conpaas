<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('cloud');
require_module('service');
require_module('ui/instance/scalaris');

class ScalarisService extends Service {

	public function __construct($data, $manager) {
		parent::__construct($data, $manager);
	}

	public function hasDedicatedManager() {
		return true;
	}

	public function sendConfiguration($params) {
		// we ignore this for now
		return '{}';
	}

	public function fetchHighLevelMonitoringInfo() {
		return false;
	}

	public function getMngmtServAddr() {
		$mngm_node = $this->getNodeInfo($this->nodesLists['scalaris'][0]);
		return $mngm_node['ip'];
	}

	public function getInstanceRoles() {
		return array('scalaris');
	}

	public function fetchStateLog() {
		return array();
	}

	public function createInstanceUI($node) {
		$info = $this->getNodeInfo($node);
		return new ScalarisInstance($info);
	}

	public function getKeysCount() {
		return '';
		$state = $this->fetchState();
		if ($state === false || !isset($state['result'])) {
			return 0;
		}
		return $state['result']['total_load'];
	}

}

?>
