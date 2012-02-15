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

require_module('logging');
require_module('http');

abstract class Service {

	protected $sid,
		$name,
		$type,
		$sw_version,
		$state,
		$creation_date,
		$manager,
		$uid,
		$cloud,
		$vmid,
		$manager_instance;

	protected $nodesLists;
	private $nodesCount = 0;

	private $reachable = false;
	private $stable = true;
	private $errorMessage = null;


	const STATE_RUNNING = 'RUNNING';
	const STATE_STOPPED = 'STOPPED';
	const STATE_TERMINATED = 'TERMINATED';
	const STATE_PREINIT = 'PREINIT';
	const STATE_INIT = 'INIT';
	const STATE_ERROR = 'ERROR';
	const STATE_ADAPTING = 'ADAPTING';

	static $state_txt = array(
		Service::STATE_RUNNING => 'running',
		Service::STATE_STOPPED => 'stopped',
		Service::STATE_TERMINATED => 'terminated',
		Service::STATE_INIT => 'initializing',
		Service::STATE_PREINIT => 'preparing',
		Service::STATE_ERROR => 'error',
		Service::STATE_ADAPTING => 'adapting',
	);

	public static function stateIsStable($remoteState) {
		return
			$remoteState != 'PROLOGUE' &&
			$remoteState != 'EPILOGUE' &&
			$remoteState != 'ADAPTING';
	}

	private function pingManager() {
		if (!isset($this->manager)) {
			return;
		}
		try {
			$state = $this->fetchState();
			if ($state !== null && isset($state['result'])) {
				$this->reachable = true;
				if (array_key_exists('state', $state['result'])) {
					$remote_state = $state['result']['state'];
					$this->stable = self::stateIsStable($remote_state);
					if ($this->state != $remote_state) {
						dlog('[State inconsistency] Remote: '.$remote_state.
							', Local: '.$this->state);
						ServiceData::updateState($this->sid, $remote_state);
						$this->state = $remote_state;
					}
				}
			}
		} catch (Exception $e) {
			dlog('error trying to connect to manager: '.$this->manager);
			dlog($e->getMessage());
		}
	}

	private function checkTimeout() {
		if ($this->state != self::STATE_PREINIT) {
			return;
		}
		$init_time = time() - strtotime($this->creation_date);
		if ($init_time > 15 * 60) {
			dlog('Switching '.$this->sid.' to ERROR state');
			ServiceData::updateState($this->sid, 'ERROR');
			$this->state = 'ERROR';
		}
	}

	public function __construct($data, $manager_instance) {
		foreach ($data as $key => $value) {
			$this->$key = $value;
		}
		$this->manager_instance = $manager_instance;
		if ($this->state == self::STATE_PREINIT) {
			$this->checkTimeout();
		}
		$this->pingManager();
		/* fetch the nodes and arrange them */
		if ($this->reachable && $this->state == self::STATE_RUNNING) {
			$this->nodesLists = $this->fetchNodesLists();
			/* compute the nodes count */
			if ($this->nodesLists !== false) {
				$selected = array();
				foreach ($this->nodesLists as $role => $nodesList) {
					foreach ($nodesList as $nodeId) {
						if (!array_key_exists($nodeId, $selected)) {
							$selected[$nodeId] = true;
							$this->nodesCount++;
						}
					}
				}
			}
		}
		if ($this->hasDedicatedManager()) {
			$this->nodesCount++;
		}
	}

	public function getErrorMessage() {
		return $this->errorMessage;
	}

	public function isReachable() {
		return $this->reachable;
	}

	public function isStable() {
		return $this->stable;
	}

	public function isRunning() {
		return $this->state == SERVICE::STATE_RUNNING;
	}

	public function isConfigurable() {
		return
			$this->reachable &&
			$this->state != self::STATE_TERMINATED &&
			$this->state != self::STATE_PREINIT &&
			$this->state != self::STATE_ERROR;
	}

	public function needsPolling() {
		return (!$this->reachable &&
				($this->state == self::STATE_RUNNING ||
				 $this->state == self::STATE_INIT ||
				 $this->state == self::STATE_PREINIT));
	}

	private function decodeResponse($json) {
		$response = json_decode($json, true);
		if ($response == null) {
			throw new Exception('null response');
		}
		if (isset($response['error']) && $response['error'] !== null) {
			$message = $response['error'];
			if (is_array($response['error'])) {
				$message = $response['error']['message'];
			}
			throw new ManagerException('Remote error: '.$message);
		}
		return $response;
	}

	protected function managerRequest($http_method, $method, array $params,
			$ping=false) {
		return HTTP::jsonrpc($this->manager, $http_method, $method, $params,
			$ping);
		$this->decodeResponse($json);
		return $json;
	}

	public function getNodeInfo($node) {
		$json_info = $this->managerRequest('get', 'get_node_info', array(
			'serviceNodeId' => $node,
		));
		$info = json_decode($json_info, true);
		if ($info == null) {
			return false;
		}
		return $info['result']['serviceNode'];
	}

	protected function fetchNodesLists() {
		if (!isset($this->manager)) {
			return false;
		}
		$json = $this->managerRequest('get', 'list_nodes', array());
		$response = json_decode($json, true);
		if ($response == null || isset($response['error'])) {
			return false;
		}
		return $response['result'];
	}

	public function fetchState() {
		$json = $this->managerRequest('get', 'get_service_info', array(), true);
		$state = json_decode($json, true);
		if ($state == null) {
			return false;
		}
		return $state;
	}

	public function fetchCodeVersions() {
		$json = $this->managerRequest('get', 'list_code_versions', array());
		$versions = json_decode($json, true);
		if ($versions == null) {
			return false;
		}
		return $versions['result']['codeVersions'];
	}

	public function fetchHighLevelMonitoringInfo() {
		$json = $this->managerRequest('get', 'get_service_performance',
			array());
		$monitoring = json_decode($json, true);
		if ($monitoring == null) {
			return false;
		}
		return $monitoring['result'];
	}

	public function getConfiguration() {
		$json_conf = $this->managerRequest('get', 'get_configuration', array());
		$responseObj = json_decode($json_conf);
		if ($responseObj == null) {
			return null;
		}
		if (!isset($responseObj->result->phpconf)) {
			return null;
		}
		return $this->conf = $responseObj->result->phpconf;
	}

 	abstract public function sendConfiguration($params);

	public function fetchStateLog() {
 		$json = $this->managerRequest('get', 'get_service_history', array());
 		$log = json_decode($json, true);
 		if ($log != null) {
 		  return $log['result']['state_log'];
 		}
 		return array();
 	}

 	public function fetchLog() {
 		$json = $this->managerRequest('get', 'getLog', array());
 		$log = json_decode($json, true);
 		return $log['result']['log'];
 	}

 	public function addServiceNodes($params) {
		if (isset($params['backend']))  {
			$params['backend'] = intval($params['backend']);
		}
		if (isset($params['web'])) {
			$params['web'] = intval($params['web']);
		}
		if (isset($params['proxy'])) {
			$params['proxy'] = intval($params['proxy']);
		}
 		return $this->managerRequest('post', 'add_nodes', $params);
 	}

 	public function removeServiceNodes($params) {
		if (isset($params['backend'])) {
			$params['backend'] = intval($params['backend']);
		}
		if (isset($params['web'])) {
			$params['web'] = intval($params['web']);
		}
		if (isset($params['proxy'])) {
			$params['proxy'] = intval($params['proxy']);
		}
 		return $this->managerRequest('post', 'remove_nodes', $params);
 	}

 	public function requestShutdown() {
 		return $this->managerRequest('post', 'shutdown', array());
 	}

 	public function requestStartup() {
 		return $this->managerRequest('post', 'startup', array());
 	}

 	/**
 	 * Deletes the service entry from the database
 	 */
 	public function terminateService() {
 		$this->manager_instance->terminate();
		ServiceData::deleteService($this->sid);
 	}

 	public function getAccessLocation() {
 		$loadbalancer = $this->getNodeInfo($this->nodesLists['proxy'][0]);
 		return 'http://'.$loadbalancer['ip'];
 	}

	public function getNodesLists() {
		return $this->nodesLists;
	}

	public function getNodesCount() {
		return $this->nodesCount;
	}

	public function getSID() {
		return $this->sid;
	}

	public function getName() {
		return $this->name;
	}

	public function getType() {
		return $this->type;
	}

	public function getTypeName() {
		return ucfirst($this->type);
	}
	
	public function getManager() {
		return $this->manager;
	}

	public function getVersion() {
		return $this->sw_version;
	}

	public function getState() {
		return $this->state;
	}

	public function getManagerVirtualID() {
		return $this->vmid;
	}

	public function getManagerInstance() {
		return $this->manager_instance;
	}

	public function getStatusText() {
		if (!isset(self::$state_txt[$this->state])) {
			return 'Unknown state: '.$this->state;
		}
		return self::$state_txt[$this->state];
	}

	public function getDate() {
		return $this->creation_date;
	}

	public function getUID() {
		return $this->uid;
	}

	public function getCloud() {
	  return $this->cloud;
	}

	public function getManagerPort() {
		return 80;
	}

	/**
	 * @return true if updated
	 */
	public function checkManagerInstance() {
		$manager_addr = $this->manager_instance->getAddress();
		if ($manager_addr !== false) {
			$manager_url = $manager_addr;
			if (strpos($manager_addr, 'http://') !== 0) {
				$manager_url = 'http://'.$manager_addr
					.':'.$this->getManagerPort();
			}
			if ($manager_url != $this->manager) {
				dlog('Service '.$this->sid.' updated manager to '.$manager_url);
				ServiceData::updateManagerAddress($this->sid, $manager_url,
					Service::STATE_INIT);
				return true;
			}
		}
		return false;
	}

	public function getManagerIP() {
		preg_match('/([\d\.]+):/', $this->manager, $matches);
		return $matches[1];
	}

	public function getInstanceRoles() {
		return false;
	}
}
