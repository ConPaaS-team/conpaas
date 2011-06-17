<?php 

require_once('logging.php');
require_once('ServiceData.php');

class Service {
	
	protected $sid,
		$name,
		$type,
		$sw_version,
		$state,
		$creation_date,
		$manager,
		$uid,
		$cloud;

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
			if ($state !== null && isset($state['opState'])) {
				$this->reachable = true;
				$this->stable = self::stateIsStable($state['state']);
			}
		} catch (Exception $e) {
			// nothing
			error_log('error trying to connect to manager');
		}
	}
	
	public function __construct($data) {
		foreach ($data as $key => $value) {
			$this->$key = $value;
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
	
	private function managerRequest($params, $method='get', $ping=false) {
		$opts = self::$CURL_OPTS;
		$opts[CURLOPT_HTTPHEADER] = array('Expect:');
		
		if ($ping) {
			$opts[CURLOPT_CONNECTTIMEOUT] = 1;
		}
		
		$url = $this->manager;
		$method = strtolower($method);
		if ($method == 'post') {
			$opts[CURLOPT_POST] = 1;
			$opts[CURLOPT_POSTFIELDS] = $params;
		} else {
			/* default is GET */
			$url .= '?'.http_build_query($params, null, '&');
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
		$json_info = $this->managerRequest(array(
			'action' => 'getServiceNodeById',
			'serviceNodeId' => $node,
		));
		$info = json_decode($json_info, true);
		if ($info == null) {
			return false;
		}
		return $info['serviceNode'];
	}
	
	private function fetchNodesLists() {
		if (!isset($this->manager)) {
			return false;
		}
		$json = $this->managerRequest(array(
			'action' => 'listServiceNodes',
		));
		$response = json_decode($json, true);
		if ($response == null) {
			return false;
		}
		unset($response['opState']);
		return $response;
	}
	
	public function fetchState() {
	   	return $this->managerRequest(
	   		array('action' => 'getState'), 
	   		'get', 
	   		true
	   );
	}
	
	public function fetchCodeVersions() {
		$json = $this->managerRequest(array('action' => 'listCodeVersions'));
		$versions = json_decode($json, true);
		if ($versions == null) {
			return false;
		}
		return $versions['codeVersions'];
	}
	
	public function fetchHighLevelMonitoringInfo() {
		$json = $this->managerRequest(array(
			'action' => 'getHighLevelMonitoring')
		);
		$monitoring = json_decode($json, true);
		if ($monitoring == null) {
			return false;
		}
		return $monitoring;
	}
	
	public function getConfiguration() {
		$json_conf = $this->managerRequest(array(
			'action' => 'getConfiguration')
		);
		$responseObj = json_decode($json_conf);
		if ($responseObj == null) {
			return null;
		}
		if (!isset($responseObj->phpconf)) {
			return null;
		}
		return $this->conf = $responseObj->phpconf;
	}
	
 	public function sendConfiguration($params) {
 		$params = array_merge($params, array(
 			'action' => 'updateConfiguration', 
 		));
 		return $this->managerRequest($params, 'post');
 	}
 	
 	public function uploadCodeVersion($params) {
 		$params = array_merge($params, array(
 			'action' => 'uploadCodeVersion'
 		));
 		return $this->managerRequest($params, 'post');
 	}
 	
 	public function fetchStateLog() {
 		$json = $this->managerRequest(array('action' => 'getStateChanges'));
 		$log = json_decode($json, true);
 		return $log['state_log'];
 	}
 	
 	public function fetchLog() {
 		$json = $this->managerRequest(array('action' => 'getLog'));
 		$log = json_decode($json, true);
 		return $log['log'];
 	}
 	
 	public function addServiceNodes($params) {
 		$params = array_merge($params, array(
 			'action' => 'addServiceNodes'
 		));
 		return $this->managerRequest($params, 'post');
 	}
 	
 	public function removeServiceNodes($params) {
 		$params = array_merge($params, array(
 			'action' => 'removeServiceNodes'
 		));
 		return $this->managerRequest($params, 'post');
 	}
 	
 	public function requestShutdown() {
 		return $this->managerRequest(
 			array('action' => 'shutdown'), 
 			'post'
 		);
 	}
 	
 	public function requestStartup() {
 		return $this->managerRequest(
 			array('action' => 'startup'),
 			'post'
 		);
 	}
 	
 	/**
 	 * Deletes the service entry from the database
 	 */
 	public function terminateService() {
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
	
}
