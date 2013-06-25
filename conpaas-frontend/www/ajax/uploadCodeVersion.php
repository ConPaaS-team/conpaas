<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('https');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

function strerror($code) {
	switch ($code) {
		case UPLOAD_ERR_INI_SIZE:
			$message = "The uploaded file exceeds maximum file size ".ini_get('upload_max_filesize');
			break;
		case UPLOAD_ERR_FORM_SIZE:
			$message = "The uploaded file exceeds the MAX_FILE_SIZE directive that was specified in the HTML form.";
			break;
		case UPLOAD_ERR_PARTIAL:
			$message = "The uploaded file was only partially uploaded.";
			break;
		case UPLOAD_ERR_NO_FILE:
			$message = "No file was uploaded.";
			break;
		case UPLOAD_ERR_NO_TMP_DIR:
			$message = "Missing a temporary folder.";
			break;
		case UPLOAD_ERR_CANT_WRITE:
			$message = "Failed to write file to disk.";
			break;
		case UPLOAD_ERR_EXTENSION:
			$message = "File upload stopped by PHP extension.";
			break;

		default:
			$message = "Unknown upload error code ".$code;
			break;
	}
	return $message;
}


$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

if (isset($_FILES['code'])) {
	$path = '/tmp/'.$_FILES['code']['name'];
	if (move_uploaded_file($_FILES['code']['tmp_name'], $path) === false) {
		$error_msg = strerror($_FILES['code']['error']);
		echo json_encode(array(
			'error' => 'could not move uploaded file: '.$error_msg
		));
		exit();
	}
	$params = array_merge($_POST, array(
		'code' => '@'.$path,
		'method' => 'upload_code_version'
	));
	try {
		$response = HTTPS::post($service->getManager(), $params);
		echo json_encode($response);
	} catch (Exception $e) {
		echo json_encode(array('error' => $e->getMessage()));
	}
	unlink($path);
} else if (isset($_GET['url'])) {
	$name = basename($_GET['url']);

	$path = '/tmp/'.$name;

	$ch = curl_init();

	curl_setopt($ch, CURLOPT_URL, $_GET['url']);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
	curl_setopt($ch, CURLOPT_HEADER, 0);

	$out = curl_exec($ch);

	curl_close($ch);

	$fp = fopen($path, 'w');
	fwrite($fp, $out);
	fclose($fp);

	$params = array_merge($_POST, array(
		'code' => '@'.$path,
		'method' => 'upload_code_version'
	));
	try {
		$response = HTTPS::post($service->getManager(), $params);
		echo json_encode($response);
	} catch (Exception $e) {
		echo json_encode(array('error' => $e->getMessage()));
	}
	unlink($path);
} else {
	echo json_encode(array(
		'error' => 'file was not uploaded (e.g. file size exceeded)'
	));
	exit();
}

?>
