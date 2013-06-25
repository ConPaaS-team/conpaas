<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('cloud');
require_module('service');
require_module('ui/instance/hadoop');

class HadoopService extends Service {

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

	public function fetchStateLog() {
		return array();
	}

	public function needsPolling() {
		return parent::needsPolling() || $this->state == self::STATE_INIT;
	}

	public function getInstanceRoles() {
		return array('masters', 'workers');
	}

	public function getAccessLocation() {
		$master_node = $this->getNodeInfo($this->nodesLists['masters'][0]);
		return 'http://'.$master_node['ip'];
	}

	public function createInstanceUI($node) {
		$info = $this->getNodeInfo($node);
		if ($this->nodesLists !== false) {
			foreach ($this->nodesLists as $role => $nodesList) {
				if (in_array($info['id'], $nodesList)) {
					$info[$role] = 1;
				}
			}
		}
		return new HadoopInstance($info);
	}

	public static function getNamenodeAttr($info, $name) {
		preg_match('/'.$name.'\<td id="col2"> :<td id="col3"> ([^\<]+)\</',
			$info, $matches);
		return $matches[1];
	}

	public function getNamenodeData() {
		$master_addr = $this->getAccessLocation();
		$info = file_get_contents($master_addr.':50070/dfshealth.jsp');
		$capacity = self::getNamenodeAttr($info, 'Configured Capacity');
		$used = self::getNamenodeAttr($info, 'DFS Used');
		return array(
			'capacity' => $capacity,
			'used' => $used,
		);
	}

}

?>
