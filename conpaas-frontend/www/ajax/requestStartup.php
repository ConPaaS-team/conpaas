<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('service');
require_module('service/factory');

try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}
	if (!array_key_exists('cloud', $_POST)){
		throw new Exception('To start a service a cloud must be selected');
	}
    $sid = $_POST['sid'];
    $cloud = $_POST['cloud'];
	$service_data = ServiceData::getServiceById($sid);
	$service = ServiceFactory::create($service_data);
	if($service->getUID() !== $_SESSION['uid']) {
	    throw new Exception('Not allowed');
	}
	$response = $service->requestStartup(array('cloud' => $cloud));
	$obj = json_decode($response, true);
	echo json_encode($obj['result']);
} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}
