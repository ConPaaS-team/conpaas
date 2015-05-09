<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('logging');



try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}
	
	$res = json_decode(HTTPS::get(Conf::DIRECTOR . '/list_resources', false, $_SESSION['uid']));
	
	echo json_encode(array(
		'data' => $res
		
	));
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array('error' => $e->getMessage()));
}
