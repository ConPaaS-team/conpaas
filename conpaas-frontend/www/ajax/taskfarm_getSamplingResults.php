<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('ui');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

try {
	$sampling_results = $service->fetchSamplingResults();
	if ($sampling_results === false) {
		echo json_encode(array());
		exit;
	}
	for ($i = 0; $i < count($sampling_results); $i++) {
		$sampling = &$sampling_results[$i];
		$utc_ts = intval($sampling['timestamp'] / 1000);
		$sampling['name'] = 'sampled '.
			TimeHelper::timeRelativeDescr($utc_ts).' ago';
	}
	echo json_encode($sampling_results);
} catch (Exception $e) {
	echo json_encode(array('error' => $e->getMessage()));
	exit();
}
