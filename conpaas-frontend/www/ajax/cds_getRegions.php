<?php

require_once('../__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');

try {
	if (!isset($_GET['sid'])) {
		throw new Exception('SID not specified');
	}
	$sid = $_GET['sid'];
	$service_data = ServiceData::getServiceById($sid);
	$cds = ServiceFactory::create($service_data);
	$clouds = $cds->joinRegionsWithSnapshot();
	$regions = array();
	foreach ($clouds as $cloud) {
		foreach ($cloud->regions as $region) {
			$regions []= array(
				'state' => $region->state,
				'edge_locations' => count($region->edge_locations)
			);
		}
	}
	echo json_encode($regions);
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}