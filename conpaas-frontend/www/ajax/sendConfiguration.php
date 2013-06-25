<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('service');
require_module('service/factory');

try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}

	$sid = $_POST['sid'];
	$service_data = ServiceData::getServiceById($sid);
	$service = ServiceFactory::create($service_data);

	if($service->getUID() !== $_SESSION['uid']) {
	    throw new Exception('Not allowed');
	}

	/*
	 * HACK: PHP translates 'conf.max_limit' into 'conf_max_limit',
	 * so we need to fix this before we send the request to the
	 * manager.
	 */

	unset($_POST['sid']);
	$response = $service->sendConfiguration($_POST);
	echo $response;
} catch (Exception $e) {
	echo json_encode(array('error' => $e->getMessage()));
}

?>
