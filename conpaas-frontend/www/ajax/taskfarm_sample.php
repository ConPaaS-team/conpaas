<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('http');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

function unlink_paths($paths) {
	foreach ($paths as $file => $path) {
		$path = str_replace('@', '', $path);
		unlink($path);
	}
}

$paths = array();
foreach (array('botFile') as $file) {
	$path = $_FILES[$file]['tmp_name'];
	// build the cURL parameter
	$paths[$file] = '@'.$path;
}
$params = array_merge($_POST, $paths);
try {
	$params['method'] = 'start_sampling';
	$json_response = HTTP::post($service->getManager() . ':' . $service->getManagerPort(), $params);
	$response = json_decode($json_response, true);
	if (array_key_exists('result', $response)) {
		$response = $response['result'];
	}
	echo json_encode($response);
} catch (Exception $e) {
	echo json_encode(array('error' => $e->getMessage()));
}
unlink_paths($paths);
