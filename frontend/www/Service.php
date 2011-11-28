<?php 
  // Copyright (C) 2010-2011 Contrail consortium.
  //
  // This file is part of ConPaaS, an integrated runtime environment 
  // for elastic cloud applications.
  //
  // ConPaaS is free software: you can redistribute it and/or modify
  // it under the terms of the GNU General Public License as published by
  // the Free Software Foundation, either version 3 of the License, or
  // (at your option) any later version.
  //
  // ConPaaS is distributed in the hope that it will be useful,
  // but WITHOUT ANY WARRANTY; without even the implied warranty of
  // MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  // GNU General Public License for more details.
  //
  // You should have received a copy of the GNU General Public License
  // along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.

require_once('logging.php');
require_once('ServiceData.php');

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
		$cloud_instance;

	private $nodesLists;
	private $nodesCount = 0;
	
	private $reachable = false;
	private $stable = true;
	
	const STATE_RUNNING = 0;
	const STATE_STOPPED = 1;
	const STATE_TERMINATED = 2;
	const STATE_PREINIT = 3;
	const STATE_INIT = 4;
	const STATE_ERROR = 5;
	
	static $state_txt = array(
		Service::STATE_RUNNING => 'running',
		Service::STATE_STOPPED => 'stopped',
		Service::STATE_TERMINATED => 'terminated',
		Service::STATE_INIT => 'initializing',
		Service::STATE_PREINIT => 'preparing',
		Service::STATE_ERROR => 'error',
	);
	
	private static $CURL_OPTS = array(
    	CURLOPT_CONNECTTIMEOUT => 10,
    	CURLOPT_RETURNTRANSFER => true,
    	CURLOPT_TIMEOUT        => 60,
	);
	
	public static function stateIsStable($remoteState) {
		return
			$remoteState != 'PROLOGUE' &&
			$remoteState != 'EPILOGUE' && 
			$remoteState != 'ADAPTING' 
		;
	}
	
	private function pingManager() {
		if (!isset($this->manager)) {
			return;
		}
		try {
			$json = $this->fetchState();
			$state = json_decode($json, true);
			if ($state !== null && isset($state['result'])) {
				$this->reachable = true;
				$this->stable = self::stateIsStable($state['result']['state']);
			}
		} catch (Exception $e) {
			// nothing
			error_log('error trying to connect to manager');
		}
	}
	
	public function __construct($data, $cloud_instance) {
		foreach ($data as $key => $value) {
			$this->$key = $value;
		}
		$this->cloud_instance = $cloud_instance;
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
			$this->state != self::STATE_PREINIT;
	}
	
	public function needsPolling() {
		return (!$this->reachable && 
				($this->state == self::STATE_RUNNING || 
				 $this->state == self::STATE_INIT ||
				 $this->state == self::STATE_PREINIT));
	}
	
	protected function managerRequest($method, $params, $http_method='get', $ping=false, $rpc=true) {
		$opts = self::$CURL_OPTS;
		if ($rpc) {
		  $opts[CURLOPT_HTTPHEADER] = array('Expect:', 'Content-Type: application/json');
		}
		else {
		  $opts[CURLOPT_HTTPHEADER] = array('Expect:');
		}
		if ($ping) {
			$opts[CURLOPT_CONNECTTIMEOUT] = 1;
		}
		
		$url = $this->manager;
		$http_method = strtolower($http_method);
		if ($http_method == 'post') {
			$opts[CURLOPT_POST] = 1;
			if ($rpc) {
  			  $opts[CURLOPT_POSTFIELDS] = json_encode(array(
  							'method' => $method,
  							'params' => $params,
  							'id' =>1 ));
			}
			else {
			  $opts[CURLOPT_POSTFIELDS] = array_merge($params, array('method' => $method));
			}
		} else {
			/* default is GET */
			$url .= '?'.http_build_query(
					array(
						'method' => $method,
						'params' => json_encode($params),
						'id' => 1),
					null, '&');
		}
		$opts[CURLOPT_URL] = $url;
		
		$conn = curl_init();
		curl_setopt_array($conn, $opts);
		$result = curl_exec($conn);
		if ($result === false) {
			$e = new Exception(
			'Error sending cURL request to '.$url.' '.
			'Error code: '.curl_errno($conn).' '.
			'Error msg: '.curl_error($conn)
			);
			curl_close($conn);
			throw $e;
		}
		curl_close($conn);
		return $result;
	}
	
	public function getNodeInfo($node) {
		$json_info = $this->managerRequest('get_node_info', array(
			'serviceNodeId' => $node,
		));
		$info = json_decode($json_info, true);
		if ($info == null) {
			return false;
		}
		return $info['result']['serviceNode'];
	}
	
	private function fetchNodesLists() {
		if (!isset($this->manager)) {
			return false;
		}
		$json = $this->managerRequest('list_nodes', array());
		$response = json_decode($json, true);
		if ($response == null || $response['error'] != null) {
			return false;
		}
		return $response['result'];
	}
	
	public function fetchState() {
	   	$ret = $this->managerRequest(
	   	    'get_service_info',
	   		array(), 
	   		'get', 
	   		true
	   );
	   return $ret;
	}
	
	public function fetchCodeVersions() {
		$json = $this->managerRequest('list_code_versions', array());
		$versions = json_decode($json, true);
		if ($versions == null) {
			return false;
		}
		return $versions['result']['codeVersions'];
	}
	
	public function fetchHighLevelMonitoringInfo() {
		$json = $this->managerRequest('get_service_performance', array());
		$monitoring = json_decode($json, true);
		if ($monitoring == null) {
			return false;
		}
		return $monitoring['result'];
	}
	
	public function getConfiguration() {
		$json_conf = $this->managerRequest('get_configuration', array());
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
 	
 	public function uploadCodeVersion($params) {
 		return $this->managerRequest('upload_code_version', $params, 'post', false, false);
 	}
 	
 	public function fetchStateLog() {
 		$json = $this->managerRequest('get_service_history', array());
 		$log = json_decode($json, true);
 		if ($log != null) {
 		  return $log['result']['state_log'];
 		}
 		else return array();
 	}
 	
 	public function fetchLog() {
 		$json = $this->managerRequest('getLog', array());
 		$log = json_decode($json, true);
 		return $log['result']['log'];
 	}
 	
 	public function addServiceNodes($params) {
		if (isset($params['backend'])) $params['backend'] = intval($params['backend']);
		if (isset($params['web'])) $params['web'] = intval($params['web']);
		if (isset($params['proxy'])) $params['proxy'] = intval($params['proxy']);
 		return $this->managerRequest('add_nodes', $params, 'post');
 	}
 	
 	public function removeServiceNodes($params) {
		if (isset($params['backend'])) $params['backend'] = intval($params['backend']);
		if (isset($params['web'])) $params['web'] = intval($params['web']);
		if (isset($params['proxy'])) $params['proxy'] = intval($params['proxy']);
 		return $this->managerRequest('remove_nodes', $params, 'post');
 	}
 	
 	public function requestShutdown() {
 		return $this->managerRequest('shutdown', array(), 'post');
 	}
 	
 	public function requestStartup() {
 		return $this->managerRequest('startup', array(), 'post');
 	}
 	
 	/**
 	 * Deletes the service entry from the database
 	 */
 	public function terminateService() {
 	  $this->cloud_instance->terminateService();
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
	
	public function getManager() {
		return $this->manager;
	}
	
	public function getVersion() {
		return $this->sw_version;
	}
	
	public function getState() {
		return $this->state;
	}
	
	public function getCloud() {
		return $this->cloud;
	}
	
	public function getStatusText() {
		return self::$state_txt[$this->state];
	}
	
	public function getDate() {
		return $this->creation_date;
	}
	
	public function getUID() {
		return $this->uid;
	}
	
	public function getCloudInstance() {
	  return $this->cloud_instance;
	}
	
	/**
	 * @return true if updated 
	 */
	public function checkManagerInstance() {
		$manager_addr = $this->cloud_instance->getManagerAddress();
		if ($manager_addr !== false) {
			$manager_url = 'http://'.$manager_addr.':80';
			if ($manager_url != $this->manager) {
				ServiceData::updateManagerAddress($this->sid, $manager_url);
				return true;
			}
		}
		return false;
	}
}


class PHPService extends Service {
  public function __construct($data, $cloud_instance) {
    parent::__construct($data, $cloud_instance);
  }
  
  public function sendConfiguration($params) {
    return $this->managerRequest('update_php_configuration', $params, 'post');
  }
}

class JavaService extends Service {
  public function __construct($data, $cloud_instance) {
    parent::__construct($data, $cloud_instance);
  }
  
  public function sendConfiguration($params) {
    return $this->managerRequest('update_java_configuration', $params, 'post');
  }
}
