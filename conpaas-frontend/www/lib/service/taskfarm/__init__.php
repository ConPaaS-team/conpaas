<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('cloud');
require_module('service');
require_module('logging');
require_module('http');

class TaskFarmService extends Service {

	private $cached_state = null;

	public function __construct($data, $manager) {
		parent::__construct($data, $manager);
	}

	/* 
	 * Temporary:
	 *
	 * Overrode this function to send HTTP requests,
	 * not HTTPS
	 *
	 */
	protected function managerRequest($http_method, $method, array $params,
			$ping=false) {
		$json = HTTP::jsonrpc($this->manager . ':' . $this->getManagerPort(), 
            $http_method, $method, $params, $ping);
		$this->decodeResponse($json, $method);
		return $json;
	}
	
	/* 
	 * Temporary:
	 *
	 * Overrode this function to send HTTP requests,
	 * not HTTPS
	 *
	 */

	private function decodeResponse($json, $method) {
		$response = json_decode($json, true);
		if ($response == null) {
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
        //########################
	
	
	public function getTypeName() {
		return 'TaskFarm';
	}

	public function isDemo() {
		return $this->isMode('DEMO');
	}

	public function isReal() {
		return $this->isMode('REAL');
	}

	public function isDemoNotSet() {
		return $this->isMode('NA');
	}

	protected function isMode($mode) {
		$state = $this->getCachedState();
		if ($state['mode'] === $mode) {
			return true;
		}
		return false;
	}

	public function getCachedState() {
		if ($this->cached_state == null) {
			$state_response = $this->fetchState();
			$this->cached_state = $state_response['result'];
		}
		return $this->cached_state;
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

	public function getNodeInfo($node) {
		return false;
	}

	public function getAccessLocation() {
		return false;
	}

	/**
	 * TODO: request implementation of this call in the TaskFarm backend
	 */
	protected function fetchNodesLists() {
		return array('manager' => array());
	}

	public function terminateService() {
		$this->terminateWorkers();
		parent::terminateService();
	}

	public function terminateWorkers() {
		$json = $this->managerRequest('post', 'terminate_workers', array(),
			true);
		$response = json_decode($json, true);
		return $response['result'];
	}

	public function setMode($mode) {
		$json = $this->managerRequest('post', 'set_service_mode',
			array($mode), true);
		$response = json_decode($json, true);
		return $response['result'];
	}

	public function	startExecution($schedulesFile, $scheduleNo) {
		$json = $this->managerRequest('post', 'start_execution', array(
			$schedulesFile, $scheduleNo));
		$result = json_decode($json, true);
		if (!array_key_exists('result', $result)) {
			if (array_key_exists('error', $result)) {
				dlog('startExecution(): '.$result);
				throw new Exception($result['error']['message']);
			}
			return false;
		}
		$result = $result['result'];
		if (array_key_exists('error', $result)) {
			throw new Exception('Error running execution: '.
				$result['error']);
		}
		return $result;
	}

	public function fetchSamplingResults() {
		$json = $this->managerRequest('post', 'get_sampling_results', array());
		$result = json_decode($json, true);
		$sampling_results = array();
		$sampling_results []= json_decode($result['result'], true);
		if (!isset($sampling_results[0])) {
			return false;
		}
		return $sampling_results;
	}

	public function hasSamplingResults() {
		try {
			$sampling_results = $this->fetchSamplingResults();
			return $sampling_results !== false && count($sampling_results) > 0;
		} catch (Exception $e) {
			dlog($e->getMessage());
		}
		return false;
	}

	public function isConfigurable() {
		return true;
	}

	public function hasDedicatedManager() {
		return true;
	}

	public function fetchHighLevelMonitoringInfo() {
		return array();
	}

	 public function fetchStateLog() {
	 	return array();
	 }

	public function sendConfiguration($params) {
		// ignore for now
	}

	public function getManagerPort() {
		return 8475;
	}

	public function toArray() {
		try {
			$state = $this->fetchState();
			$state = $state['result'];
			return array_merge(parent::toArray(), array(
				'moneySpent' => $state['moneySpent'],
				'completedTasks' => $state['noCompletedTasks'],
				'totalTasks' => $state['noTotalTasks']
			));
		} catch (Exception $e) {
			dlog($e->getMessage());
			return parent::toArray();
		}
	}
}
