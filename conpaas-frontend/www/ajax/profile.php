<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('__init__.php');
require_module('https');
require_module('application');
// require_module('service');
// require_module('service/factory');

try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}

	if (!isset($_SESSION['aid'])) {
		throw new Exception('The aid is not in the session');
	}

	$aid = $_GET['aid'];
	$iterations = $_GET['iterations'];
	$debug = $_GET['debug'];
	$monitor = $_GET['monitor'];

	$application_data = ApplicationData::getApplicationById($_SESSION['uid'], $aid);
	$application = new Application($application_data);

	$res = 	$application->profile($iterations, $debug, $monitor);
	
	echo json_encode($res);

	
} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}
?>