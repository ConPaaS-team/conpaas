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