<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('db');
require_module('user');
require_module('service');
require_module('service/factory');

try {
	if ($_SERVER['REQUEST_METHOD'] != 'POST') {
		throw new Exception('Only calls with POST method accepted');
	}

	if (!isset($_SESSION['aid'])) {
		throw new Exception('Application is not valid');
	}

	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}

	$aid = $_SESSION['aid'];
	
	session_write_close();

	$res = json_decode(HTTPS::post(Conf::DIRECTOR . '/startapp/' . $aid,
		array(), false, $_SESSION['uid']));

	if (!$res) {
		throw new Exception('User not logged in');
	}

	if (property_exists($res, 'msg')) {
		echo json_encode(array('error' => $res->msg));
	}else{
		echo json_encode(array('start' => 1));
	}
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}
