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

$sid = $_POST['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

if (!isset($_POST['sshkey'])) {
	echo json_encode(array(
		'error' => 'ssh key not uploaded'
	));
	exit();
}

/* Check if the uploaded key is valid */


$tmp = array_search('uri', @array_flip(stream_get_meta_data($GLOBALS[mt_rand()]=tmpfile())));
file_put_contents($tmp, $_POST['sshkey']);

$params = array(
	'key' => '@'.$tmp,
	'method' => 'upload_authorized_key'
);

try {
	$response = HTTPS::post($service->getManager(), $params);
	echo json_encode($response);
} catch (Exception $e) {
	echo json_encode(array('error' => $e->getMessage()));
}
?>
