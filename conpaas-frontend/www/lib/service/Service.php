<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('logging');
require_module('https');

class Service {

	protected $sid,
		$name,
		$type,
		$sw_version,
		$state,
		$creation_date,
		// $manager,
		// $uid,
		$cloud,
		// $vmid,
		// $manager_instance;
		$application;

	protected $nodesLists;
	private $nodesCount = 0;

	private $cached_state = null;
	private $reachable = false;
	private $stable = true;

	private $errorMessage = null;
	protected $volumes = null;

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
		// dlog($this->manager.': '.$e->getMessage());
		if (!isset($this->application)) {
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
			dlog(__FILE__.': error trying to connect to manager '.$this->application->getManager().': '.$e->getMessage());
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

	public function __construct($data, $application) {
		foreach ($data as $key => $value) {
			$this->$key = $value;
		}

        // if ($this->type === 'taskfarm') {
        // 	$this->manager = 'http://'.$application->getManager();
        //     // $this->manager = 'http://'.$this->manager;
        // }
        // else {
        // 	$this->manager = 'https://'.$application->getManager();
        //     // $this->manager = 'https://'.$this->manager;
        // }

		// $this->manager_instance = $manager_instance;
		$this->application = $application;
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

	protected function managerRequest($http_method, $method, array $params, $ping=false) {
		return $this->application->managerRequest($http_method, $method, $this->sid, $params, $ping);
	}

	public function getNodeInfo($node) {
		$json_info = $this->managerRequest('get', 'get_node_info', array(
			'serviceNodeId' => $node,
		));
		$info = json_decode($json_info, true);
		if ($info == null) {
			return false;
		}
		$info = $info['result']['serviceNode'];
		$info['sid'] = $this->sid;
		return $info;
	}

	protected function fetchNodesLists() {
		if (! $this->application->isManagerSet()) {
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
 		$json = $this->managerRequest('get', 'get_manager_log', array());
 		$log = json_decode($json, true);
 		return $log['result']['log'];
 	}

	public function fetchAgentLog($params) {
		$json = $this->application->managerRequest('get', 'get_agent_log', 0, $params);
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
        $data = array();
        $data['nodes'] = $nodes;
        if ($command == 'add_nodes') {
            $data['cloud'] = $params['cloud'];
        }
 		// return $this->managerRequest('post', $command, $nodes);
 		$data['service_id'] = $this->sid;
 		return $this->application->managerRequest('post', $command, 0, $data);
 	}

 	public function uploadStartupScript($script) {
 		$command = 'upload_startup_script';
 		$data = array();
 		$data['service_id'] = 0;
 		$data['sid'] = $this->sid;
 		$data['script'] = $script;
 		return $this->application->managerRequest('upload', $command, 0, $data);
 	}

 	public function getStartupScript() {
 		$command = 'get_startup_script';
 		$data = array();
 		$data['sid'] = $this->sid;
 		return HTTPS::jsonrpc($this->getManager(), 'get', $command, 0, $data, false);
 		// return $this->application->managerRequest('get', $command, 0, $data);
 	}

 	public function addServiceNodes($params) {
 		return $this->changeNodes('add_nodes', $params);
 	}

 	public function removeServiceNodes($params) {
 		return $this->changeNodes('remove_nodes', $params);
 	}

 	public function requestShutdown() {
 		$params['service_id'] = $this->sid;
 		return $this->application->managerRequest('post', 'stop_service', 0, $params);
 		// return $this->managerRequest('post', 'stop', array());
 	}

 	public function requestStartup($params) {
 		$params['service_id'] = $this->sid;
 		return $this->application->managerRequest('post', 'start_service', 0, $params);
 		// return $this->managerRequest('post', 'startup', $params);
 	}

 	/**
 	 * Deletes the service entry from the database
 	 */
 	public function removeService() {

        $res = HTTPS::post(Conf::DIRECTOR . '/remove',
            array( 'app_id' => $this->application->getAID(), 'service_id' => $this->sid ), true, $this->application->getUID());

        if (!json_decode($res)) {
            throw new Exception('Error removing service '. $this->sid);
        }
 	}

 	public function listVolumes() {
		$json = $this->application->managerRequest('post', 'list_volumes', 0, array('service_id'=> $this->sid));
		$volumes = json_decode($json, true);
		if ($volumes == null) {
			return false;
		}
		
		return $volumes['result']['volumes'];
	}

	public function createVolume($params) {
		$params['volumeSize'] = intval($params['volumeSize']);
		$resp = $this->application->managerRequest('post', 'create_volume', 0, $params);
		return $resp;
	}

	public function deleteVolume($params) {
		$resp = $this->application->managerRequest('post', 'delete_volume', 0, $params);
		return $resp;
	}


	public function updateVolumes() {
		$this->volumes = null;
		if (!$this->isRunning()) {
			return;
		}
		$volumes = $this->listVolumes();
		if ($volumes === false) {
			return;
		}
		usort($volumes, function ($a, $b) {
			return strcmp($a['vol_name'], $b['vol_name']);
		});
		$this->volumes = array();
		if ($this->nodesLists !== false) {
			foreach ($this->nodesLists as $role => $nodesList) {
				foreach ($nodesList as $node) {
					$this->volumes[$node] = array_values(array_filter($volumes,
						function($volume) use($node) {
							return $volume['vm_id'] === $node;
						}
					));
				}
			}
		}
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
		return $this->application->getManager();
	}

	public function getManagerIP() {
		return $this->application->getManagerIP();
	}

	public function getVersion() {
		return $this->sw_version;
	}

	public function getState() {
		return $this->state;
	}

	// public function getManagerInstance() {
	// 	return $this->manager_instance;
	// }
	public function getApplication() {
		return $this->application;
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
		return $this->application->getUID();
	}

	public function getCloudName() {
	  return $this->cloud;
	}

	public function getManagerPort() {
		return 443;
	}

	/**
	 * @return true if updated
	 */
	public function checkManagerInstance() {
		// $manager_addr = $this->manager_instance->getHostAddress();
		$manager_addr = $this->application->getManager();
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
