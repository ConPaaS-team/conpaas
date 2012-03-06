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
require_module('ui/instance/scalarix');

class ScalarixService extends Service {

	public function __construct($data) {
		parent::__construct($data, new ScalarixManager($data));
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

	protected function fetchNodesLists() {
		if (!isset($this->manager)) {
			return false;
		}
		$json = $this->managerRequest('post', 'list_nodes', array());
		$response = json_decode($json, true);
		if ($response === null || isset($response['error'])) {
			return false;
		}
		return array('peers' => $response['result']['peers']);
	}

	public function getNodeInfo($node) {
		$json_info = $this->managerRequest('post', 'get_node_info',
			array($node));
		$info = json_decode($json_info, true);
		if ($info == null || !isset($info['result'])) {
			return false;
		}
		$info = $info['result'];
		// HACK
		if (isset($info['result'])) {
			$info = $info['result'];
		}
		$info['id'] = $node;
		return $info;
	}

	public function addServiceNodes($params) {
		if (!isset($params['scalarix'])) {
			throw new Exception('Number of nodes not specified');
		}
		return $this->managerRequest('post', 'add_nodes',
			array($params['scalarix']));
	}

	public function removeServiceNodes($params) {
		if (!isset($params['scalarix'])) {
			throw new Exception('Number of nodes not specified');
		}
		return $this->managerRequest('post', 'remove_nodes',
			array($params['scalarix']));
	}

	public function createInstanceUI($node) {
		$info = $this->getNodeInfo($node);
		return new ScalarixInstance($info);
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

	/**
	 * @return true if updated
	 */
	public function checkManagerInstance() {
		try {
			$state = $this->fetchState();
		} catch (Exception $e) {
			dlog($e->getMessage());
			return false;
		}
		if ($state === false) {
			return false;
		}
		if ($state['result']['state'] == 'RUNNING') {
			ServiceData::updateState($this->sid, Service::STATE_RUNNING);
			return true;
		}
		return false;
	}

	public function requestShutdown() {
		// ignore
	}

	public function requestStartup() {
		// ignore
	}

	public function getKeysCount() {
		$state = $this->fetchState();
		if ($state === false || !isset($state['result'])) {
			return 0;
		}
		return $state['result']['total_load'];
	}

}

?>