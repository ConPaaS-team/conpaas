<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('cloud');
require_module('service');
require_module('ui/instance/xtreemfs');

class XtreemFSService extends Service {

	public function __construct($data, $manager) {
		parent::__construct($data, $manager);
	}


	public function sendConfiguration($params) {
		return '{}';
	}

	public function fetchHighLevelMonitoringInfo() {
		return false;
	}

	public function getInstanceRoles() {
		return array('dir', 'mrc', 'osd');
	}

	public function needsPolling() {
		return parent::needsPolling() || $this->state == self::STATE_INIT;
	}

	public function createInstanceUI($info) {
		return new XtreemFSInstance($info);
	}

	public function createXFSVolume($volumeName,$owner) {
		$resp = $this->managerRequest('post', 'createVolume', array(
                'volumeName' => $volumeName,
                'owner' => $owner));
		return $resp;
	}
	public function deleteXFSVolume($volumeName) {
		$resp = $this->managerRequest('post', 'deleteVolume', array(
				'volumeName' => $volumeName));
		return $resp;
	}

 	public function viewXFSVolumes() {
 		$json = $this->managerRequest('get', 'listVolumes', array());
 		$volumes = json_decode($json, true);
 		return $volumes['result']['volumes'];
 	}

	public function listXFSVolumes() {
		$volumesText = $this->viewXFSVolumes();
		preg_match_all("/^\t(.+)\t->\t(.+)$/m", $volumesText,
				$out, PREG_PATTERN_ORDER);
		$volumes = array();
		for($i = 0; $i < count($out[1]); $i++) {
			$volume['volumeName'] = $out[1][$i];
			$volume['volumeUUID'] = $out[2][$i];
			$volumes[$i] = $volume;
		}
		if ($volumes) {
			usort($volumes, function ($a, $b) {
				return strcmp($a['volumeName'], $b['volumeName']);
			});
		}
		return $volumes;
	}

	public function getAccessLocation() {
		$dir_node = $this->getNodeInfo($this->nodesLists['dir'][0]);
		return $dir_node['ip'];
	}

}

?>
