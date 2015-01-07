<?php
/* Copyright (C) 2010-2014 by Contrail Consortium. */



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

	unset($_POST['sid']);
	$response = HTTPS::jsonrpc($service->getManager(), 'post', 'delete_code_version', $_POST);
	echo $response;
} catch (Exception $e) {
	echo json_encode(array('error' => $e->getMessage()));
}

?>
