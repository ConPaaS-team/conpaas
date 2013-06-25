<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('cloud');
require_module('service');
require_module('ui/instance/xtreemfs');

class XtreemFSService extends Service {

	public function __construct($data, $manager) {
		parent::__construct($data, $manager);
	}

	public function hasDedicatedManager() {
		return true;
	}

	public function sendConfiguration($params){
		return '{}';
	}

	public function fetchHighLevelMonitoringInfo() {
		return false;
	}

	public function getInstanceRoles() {
		return array('dir', 'mrc','osd');
	}

	public function fetchStateLog() {
		return array();
	}

	public function needsPolling() {
		return parent::needsPolling() || $this->state == self::STATE_INIT;
	}

	public function createInstanceUI($node) {
		$info = $this->getNodeInfo($node);
		return new XtreemFSInstance($info);
	}

	public function createVolume($volumeName,$owner) {
		$resp = $this->managerRequest('post','createVolume',array(
                'volumeName' => $volumeName,
                'owner' => $owner));
		return $resp;
	}
	public function deleteVolume($volumeName) {
		$resp = $this->managerRequest('post','deleteVolume',array(
				'volumeName' => $volumeName));
		return $resp;
	}

 	public function viewVolumes() {
 		$json = $this->managerRequest('get', 'listVolumes', array());
 		$volumes = json_decode($json, true);
 		return $volumes['result']['volumes'];
 	}
}

?>
