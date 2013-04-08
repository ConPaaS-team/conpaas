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

require_module('logging');
require_module('https');

class Service {

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

	private $cached_state = null;
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
	const STATE_PROLOGUE = 'PROLOGUE';
	const STATE_EPILOGUE = 'EPILOGUE';

	static $state_txt = array(
		Service::STATE_RUNNING => 'running',
		Service::STATE_STOPPED => 'stopped',
		Service::STATE_TERMINATED => 'terminated',
		Service::STATE_INIT => 'initialized',
		Service::STATE_PREINIT => 'preparing',
		Service::STATE_ERROR => 'error',
		Service::STATE_ADAPTING => 'adapting',
		Service::STATE_PROLOGUE => 'prologue',
		Service::STATE_EPILOGUE => 'epilogue',
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
                           $this->state = $remote_state;
                       }
               }
			}
		} catch (ManagerException $e) {
			dlog($this->manager.': '.$e->getMessage());
			$this->errorMessage = $e->getMessage();
			$this->reachable = true;
			$this->state = self::STATE_ERROR;
		} catch (Exception $e) {
			dlog(__FILE__.': error trying to connect to manager '
				.$this->manager.': '.$e->getMessage());
		}
	}

	private function checkTimeout() {
		if ($this->state != self::STATE_INIT) {
			return;
		}
        /*
		$init_time = time() - strtotime($this->creation_date);
		if ($init_time > Conf::FAILOUT_TIME) {
			dlog('Switching '.$this->sid.' to ERROR state');
			ServiceData::updateState($this->sid, 'ERROR');
			$this->state = 'ERROR';
		}*/
	}

	public function __construct($data, $manager_instance) {
		foreach ($data as $key => $value) {
			$this->$key = $value;
		}

        if ($this->type === 'taskfarm') {
            $this->manager = 'http://'.$this->manager;
        }
        else {
            $this->manager = 'https://'.$this->manager;
        }

		$this->manager_instance = $manager_instance;
		$this->pingManager();
		if (!$this->reachable && $this->state == self::STATE_INIT) {
			$this->checkTimeout();
		}
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
				 $this->state == self::STATE_PREINIT ||
				 $this->state == self::STATE_ERROR));
	}

	private function decodeResponse($json, $method) {
		$response = json_decode($json, true);
		if ($response == null) {
			if (strlen($json) > 256) {
				$json = substr($json, 0, 256).'...[TRIMMED]';
			}
			throw new Exception('Error parsing response for '.$method
				.': "'.$json.'"');
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
		$json = HTTPS::jsonrpc($this->manager, $http_method, $method, $params,
			$ping);
		$this->decodeResponse($json, $method);
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

	public function fetchState($force_fetch=false) {
		if (!$force_fetch && $this->cached_state !== null) {
			return $this->cached_state;
		}
		$json = $this->managerRequest('get', 'get_service_info', array(), true);
		$state = json_decode($json, true);
		if ($state == null) {
			return false;
		}
		$this->cached_state = $state;
		return $this->cached_state;
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

 	private function changeNodes($command, $params) {
 		$nodes = array();
 		foreach ($this->getInstanceRoles() as $role) {
 			if (isset($params[$role])) {
 				$nodes[$role] = intval($params[$role]);
 			}
        }
        if ($command == 'add_nodes') {
            $nodes['cloud'] = $params['cloud'];
        }
 		return $this->managerRequest('post', $command, $nodes);
 	}

 	public function addServiceNodes($params) {
 		return $this->changeNodes('add_nodes', $params);
 	}

 	public function removeServiceNodes($params) {
 		return $this->changeNodes('remove_nodes', $params);
 	}

 	public function requestShutdown() {
 		return $this->managerRequest('post', 'shutdown', array());
 	}

 	public function requestStartup($params) {
 		return $this->managerRequest('post', 'startup', $params);
 	}

 	/**
 	 * Deletes the service entry from the database
 	 */
 	public function terminateService() {
 		$this->manager_instance->terminate();
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

    public function getCloudType() {
        return (int) substr($this->cloud,0,1);
    }

	public function getCloudName() {
	  return substr($this->cloud,1);
	}

	public function getManagerPort() {
		return 443;
	}

	/**
	 * @return true if updated
	 */
	public function checkManagerInstance() {
		$manager_addr = $this->manager_instance->getHostAddress();
		return $manager_addr !== false;
	}

	public function getInstanceRoles() {
		return false;
	}

	public function toArray() {
		return array(
			'sid' => $this->sid,
			'state' => $this->state,
			'cloud' => $this->cloud,
			'type' => $this->type,
			'reachable' => $this->reachable,
			'instanceRoles' => $this->getInstanceRoles(),
		);
	}
}
