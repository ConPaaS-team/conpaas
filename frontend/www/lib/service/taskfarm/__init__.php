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