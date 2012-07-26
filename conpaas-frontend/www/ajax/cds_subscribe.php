<?php

require_once('../__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');

try {
	$hosting_sid = $_POST['sid'];
	$cds_sid = $_POST['cds'];
	$subscribe = $_POST['subscribe'];
	if (!isset($hosting_sid) || !isset($cds_sid) || !isset($subscribe)) {
		throw new Exception('Missing parameter');
	}
	if ($subscribe === 'true') {
		$subscribe = true;
	} else if ($subscribe === 'false') {
		$subscribe = false;
	} else {
		throw new Exception('parameter "subscribe" must be true or false');
	}

	$hosting_service_data = ServiceData::getServiceById($hosting_sid);
	$hosting_service = ServiceFactory::create($hosting_service_data);
	if ($subscribe) {
		$cds_data = ServiceData::getServiceById($cds_sid);
		$cds = ServiceFactory::create($cds_data);
		// first subscribe to the CDS
		if ($hosting_service->isRunning()) {
			$cds->subscribe($hosting_service->getAppAddress(), 'US');
		}
		// give some time for the configuration to propagate
		sleep(5);
		$address = $cds->getManagerInstance()->getHostAddress();
		$hosting_service->cdnEnable(true, $address);
		echo json_encode(array('subscribe' => 1));
	} else {
		// unsubscribing
		if ($hosting_service->isRunning()) {
			$cds = $hosting_service->getCds();
			$cds->unsubscribe($hosting_service->getAppAddress());
		}
		$hosting_service->cdnEnable(false, '');
		echo json_encode(array('unsubscribe' => 1));
	}
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}
