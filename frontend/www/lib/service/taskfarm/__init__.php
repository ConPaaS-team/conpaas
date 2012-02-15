<?php
require_module('cloud');
require_module('service');
require_module('logging');

class TaskFarmService extends Service {

	public function __construct($data) {
		parent::__construct($data, new TaskFarmManager($data));
	}

	public function getTypeName() {
		return 'TaskFarm';
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
		dlog('terminate_workers: '.$response['result']['message']);
		return $response['result'];
	}

	public function fetchSamplingResults() {
		$json = $this->managerRequest('post', 'get_sampling_results', array());
		$result = json_decode($json, true);
		if (!array_key_exists('result', $result)) {
			if (array_key_exists('error', $result)) {
				throw new Exception($result['error']['message']);
			}
			return false;
		}
		$sampling_results = $result['result'];
		if (array_key_exists('error', $sampling_results)) {
			throw new Exception('Error fetching sampling results: '.
				$sampling_results['error']);
		}
		return $sampling_results;
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

	public function hasSamplingResults() {
		try {
			$sampling_results = $this->fetchSamplingResults();
			return count($sampling_results) > 0;
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

}