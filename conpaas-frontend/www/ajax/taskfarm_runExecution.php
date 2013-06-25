<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$sid = $_POST['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

$schedulesFile = $_POST['schedulesFile'];
$scheduleNo = $_POST['scheduleNo'];

try {
	$result = $service->startExecution($schedulesFile, $scheduleNo);
	echo json_encode($result);
} catch (Exception $e) {
	echo json_encode(array('error' => $e->getMessage()));
	exit();
}
