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
require_module('service');
require_module('ui/instance/hadoop');

class HadoopService extends Service {

	public function __construct($data) {
		parent::__construct($data, new HadoopManager($data));
	}

	public function hasDedicatedManager() {
		return false;
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

	protected function fetchNodesLists() {
		if (!isset($this->manager)) {
			return false;
		}
		$json = $this->managerRequest('post', 'list_nodes', array());
		$response = json_decode($json, true);
		if ($response == null || isset($response['error'])) {
			return false;
		}
		return $response['result'];
	}

	public function getNodeInfo($node) {
		$json_info = $this->managerRequest('post', 'get_node_info',
			array($node));
		$info = json_decode($json_info, true);
		if ($info == null || !isset($info['result'])) {
			return false;
		}
		// HACK: TODO(claudiugh) report bug
		if (isset($info['result']['result'])) {
			$info['result']['result']['id'] = $node;
			return $info['result']['result'];
		}
		$info['result']['id'] = $node;
		return $info['result'];
	}

	public function addServiceNodes($params) {
		if (!isset($params['hadoop'])) {
			throw new Exception('Number of nodes not specified');
		}
		return $this->managerRequest('post', 'add_nodes',
			array($params['hadoop']));
	}

	public function removeServiceNodes($params) {
		if (!isset($params['hadoop'])) {
			throw new Exception('Number of nodes not specified');
		}
		return $this->managerRequest('post', 'remove_nodes',
			array($params['hadoop']));
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

	public function fetchState() {
		$json = $this->managerRequest('post', 'get_service_info', array(),
			true);
		$state = json_decode($json, true);
		if ($state == null) {
			return false;
		}
		return $state;
	}

	public function requestShutdown() {
		// ignore
	}

	public function requestStartup() {
		// ignore
	}

	public static function getNamenodeAttr($info, $name) {
		preg_match('/'.$name.'\<td id="col2"> :<td id="col3"> ([^\<]+)\</',
			$info, $matches);
		return $matches[1];
	}

	public function getNamenodeData() {
		$manager_ip = $this->getManagerIP();
		$info = file_get_contents('http://'.$manager_ip.':50070/dfshealth.jsp');
		$capacity = self::getNamenodeAttr($info, 'Configured Capacity');
		$used = self::getNamenodeAttr($info, 'DFS Used');
		return array(
			'capacity' => $capacity,
			'used' => $used,
		);
	}

}

?>