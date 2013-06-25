<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('cloud');
require_module('logging');
require_module('service');

class ContentDeliveryService extends Service {

	public function __construct($data, $manager) {
		parent::__construct($data, $manager);
	}

	public function hasDedicatedManager() {
		return true;
	}

	public function subscribe($origin, $country) {
		return $this->managerRequest('post', 'subscribe',
			array('origin' => $origin, 'country' => $country));
	}

	public function unsubscribe($origin) {
		return $this->managerRequest('post', 'unsubscribe',
			array('origin' => $origin));
	}

	public function fetchHighLevelMonitoringInfo() {
		return false;
	}

	public function getSubscribers() {
		$json = $this->managerRequest('get', 'get_subscribers', array());
		$obj = json_decode($json, true);
		$subscribers = $obj['result'];
		if (count(array_keys($subscribers)) > 0) {
			// sort the array based on timestamp
			$ts = array();
			foreach ($subscribers as $app => $details) {
				$ts []= intval($details['mtime']);
			}
			array_multisort($ts, SORT_DESC, $subscribers);
		}
		return $subscribers;
	}

	public function getSnapshot() {
		$json = $this->managerRequest('get', 'get_snapshot', array());
		$obj = json_decode($json, true);
		$edge_locations = $obj['result'];
		return $edge_locations;
	}

	public function getGroupedEdgeLocations() {
		$edge_locations = $this->getSnapshot();
		$grouped_edge_locations = array('us-east-1' => array());
		foreach ($edge_locations as $e) {
			$grouped_edge_locations['us-east-1'] []= $e;
		}
		return $grouped_edge_locations;
	}

	public function joinRegionsWithSnapshot() {
		$grouped_edge_locations = $this->getGroupedEdgeLocations();
		$clouds = CloudFactory::getAvailableClouds();
		foreach ($clouds as $cloud) {
			$cloud->regions = array();
			foreach ($cloud->getAvailableRegions() as $region) {
				$cloud->regions []= $region;
				$edge_locations = array();
				if (isset($grouped_edge_locations[$region->id])) {
					$edge_locations = $grouped_edge_locations[$region->id];
				}
				$region->edge_locations = $edge_locations;
			}
		}
		return $clouds;
	}

	public function getLog() {
		$json = $this->managerRequest('get', 'get_log', array('lines' => 10));
		$obj = json_decode($json, true);
		return $obj['result'];
	}

	public function fetchStateLog() {
		return array();
	}

}
