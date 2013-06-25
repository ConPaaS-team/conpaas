<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('__init__.php');
require_module('db');
require_module('user');
require_module('service');
require_module('service/factory');

try {

	if ($_SERVER['REQUEST_METHOD'] != 'POST') {
		throw new Exception('Only calls with POST method accepted');
	}

    if (!array_key_exists('type', $_POST)){
		throw new Exception('Missing type parameter');
	}else if (!array_key_exists('cloud', $_POST)){
		throw new Exception('Missing cloud parameter');
	}


	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}

	if (!isset($_SESSION['aid'])) {
		throw new Exception('Application id is not set');
	}

	$appid = $_SESSION['aid'];
	$type = $_POST['type'];
    $cloud= $_POST['cloud'];

	$res = json_decode(HTTPS::post(Conf::DIRECTOR . '/start/' . $type. '/' . $cloud,
	    array( 'appid' => $appid ), false, $_SESSION['uid']));

    if (!$res) {
        throw new Exception('User not logged in');
    }

    /* error creating new service */
    if (property_exists($res, 'msg')) {
        throw new Exception($res->msg);
    }

	// HACK: keep a must_reset_password flag for the MySQL service
	// we should keep this information in the service's manager state
	if ($type == 'mysql') {
		$_SESSION['must_reset_passwd_for_'.$res->sid] = true;
	}

	echo json_encode(array(
		'sid' => $res->sid,
		'create' => 1,
	));
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}
