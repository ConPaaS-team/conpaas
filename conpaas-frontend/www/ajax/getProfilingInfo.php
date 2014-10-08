<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('__init__.php');
require_module('https');
require_module('service');
require_module('service/factory');

try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}

	if (!isset($_SESSION['aid'])) {
		throw new Exception('The aid is not in the session');
	}

	$aid = $_SESSION['aid'];
	
	$sid = $_GET['sid'];
	$service_data = ServiceData::getServiceById($sid);
	$service = ServiceFactory::create($service_data);
	$info = $service->getProfilingInfo();
	

	// $res = json_decode(HTTPS::post(Conf::DIRECTOR . '/renameapp/' . $aid,
	// 	array('name' => $newname), false, $_SESSION['uid']));
    $res = array('profiling_info' => $info);
	print json_encode($res);
} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}
?>
