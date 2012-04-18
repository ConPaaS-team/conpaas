<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
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
		return HTTP::post($this->getManager(), array(
			'method' => 'load_dump',
			'mysqldump_file' => '@'.$file));
	}
}

?>
