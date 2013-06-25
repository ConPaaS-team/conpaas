<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('logging');
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

	if (isset($_FILES['dbfile'])) {
		$response = $service->loadFile($_FILES['dbfile']['tmp_name']);
	} else if (isset($_POST['url'])) {
		$name = basename($_POST['url']);

		$path = '/tmp/'.$name;

		$ch = curl_init();

		curl_setopt($ch, CURLOPT_URL, $_POST['url']);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt($ch, CURLOPT_HEADER, 0);

		$out = curl_exec($ch);

		curl_close($ch);

		$fp = fopen($path, 'w');
		fwrite($fp, $out);
		fclose($fp);

		$response = $service->loadFile($path);

		unlink($path);
	} else {
		throw new Exception('File not specified');
	}

	echo json_encode($response);
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}
