<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('cloud');
require_module('https');
require_module('service');
require_module('ui/instance/mysql');

class MysqlService extends Service {

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

	public function getInstanceRoles() {
		return array('masters', 'slaves');
	}

	public function fetchStateLog() {
		return array();
	}

	public function createInstanceUI($node) {
		$info = $this->getNodeInfo($node);
		return new MysqlInstance($info);
	}

	public function needsPasswordReset() {
		return
			isset($_SESSION['must_reset_passwd_for_'.$this->sid]);
	}

	public function setPassword($user, $password) {
		$resp = $this->managerRequest('post', 'set_password', array(
			'user' => $user,
			'password' => $password
		));
		unset($_SESSION['must_reset_passwd_for_'.$this->sid]);
		return $resp;
	}

	public function getMasterAddr() {
		$master_node = $this->getNodeInfo($this->nodesLists['masters'][0]);
		return $master_node['ip'];
	}

	public function getAccessLocation() {
		return $this->getMasterAddr().' : 3306';
	}

	public function getUsers() {
		return array('mysqldb');
	}

	public function loadFile($file) {
		return HTTPS::post($this->getManager(), array(
			'method' => 'load_dump',
			'mysqldump_file' => '@'.$file));
	}
}

?>
