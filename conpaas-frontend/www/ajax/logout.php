<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('user');

try {
	$user = new User();
	$user->closeSession();
	echo json_encode(array('logout' => 1));
} catch (Exception $e) {
	dlog($e->getMessage());
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'logout' => 0,
		'error' => $e->getMessage()
	));
}
