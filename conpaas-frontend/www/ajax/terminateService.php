<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('service');
require_module('service/factory');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

try {
	$sid = $_POST['sid'];
	$service_data = ServiceData::getServiceById($sid);
	$service = ServiceFactory::create($service_data);

    if($service->getUID() !== $_SESSION['uid']) {
        throw new Exception('Not allowed');
    }

	$service->terminateService();
	echo json_encode(array(
		'terminate' => 1,
	));
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}
