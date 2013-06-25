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

	if (!array_key_exists('aid', $_POST)) {
		throw new Exception('Missing parameters');
	}

	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}

	$aid = $_POST['aid'];

	$res = json_decode(HTTPS::post(Conf::DIRECTOR . '/delete/' . $aid,
		array(), false, $_SESSION['uid']));

	if (!$res) {
		throw new Exception('User not logged in');
	}

	echo json_encode(array(
		'delete' => 1
	));
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}
