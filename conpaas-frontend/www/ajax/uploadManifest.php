<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */

require_once("__init__.php");
require_module('db');
require_module('user');

try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}

	$specs = "";
	$app = "";
	$slo = "";
	
	if (is_uploaded_file($_FILES['manfile']['tmp_name'])) {
		$specs = file_get_contents($_FILES['manfile']['tmp_name']);
		if (is_uploaded_file($_FILES['appfile']['tmp_name'])) 
			$app = file_get_contents($_FILES['appfile']['tmp_name']);
		if (isset($_POST['slo']))
			$slo = $_POST['slo'];
		
	} else if (isset($_POST['json'])) {
		$specs = $_POST['json'];
	} else {
		throw new Exception("Error reading the manifest");
	}

	$specs = preg_replace("/\n/", "", $specs);
	$specs = preg_replace("/\t/", "", $specs);
	$app = strtoupper(bin2hex($app));

	//$res = json_decode(HTTPS::post(Conf::DIRECTOR . '/upload_manifest',
	//	array( 'manifest' => $specs, 'thread' => 1 ), false, $_SESSION['uid']));

	$res = json_decode(HTTPS::post(Conf::DIRECTOR . '/upload_manifest',
		array( 'manifest' => $specs, 'slo' => $slo, 'app_tar' => $app, 'thread' => 1 ), false, $_SESSION['uid']));

	if (!$res) {
		throw new Exception('The manifest has some errors in it');
	}

	if (property_exists($res, 'msg')) {
		throw new Exception($res->msg);
	}

	echo json_encode(array(
		'upload' => 1,
		'appid' => $res->appid,
	));
	
	
} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}

?>
