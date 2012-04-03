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

require_module('cloud');
require_module('http');
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

	public function setPassword($user, $password) {
		return $this->managerRequest('post', 'set_password', array(
			'user' => $user,
			'password' => $password
		));
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
		return HTTP::post($this->getManager(), array(
			'method' => 'load_dump',
			'mysqldump_file' => '@'.$file));
	}
}

?>