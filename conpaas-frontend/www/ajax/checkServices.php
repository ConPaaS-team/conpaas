<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('ui/service');

try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}
	$uid = $_SESSION['uid'];
	$aid = $_SESSION['aid'];

	$services_data = ServiceData::getServicesByUser($uid, $aid);
	$servicesList = new ServicesListUI(array());
	foreach ($services_data as $service_data) {
		$service = ServiceFactory::create($service_data);
		$servicesList->addService($service);
		if (!$service->isReachable()) {
			$service->checkManagerInstance();
		}
	}
	$services_data = $servicesList->toArray();
	echo json_encode(array(
		'data' => $services_data,
		'html' => $servicesList->render()
	));
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array('error' => $e->getMessage()));
}
