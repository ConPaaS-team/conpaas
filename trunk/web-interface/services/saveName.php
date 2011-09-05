<?php

require_once('../__init__.php');
require_once('../ServiceFactory.php');
require_once('../ServiceData.php');

if (!isset($_SESSION['uid'])) {
    throw new Exception('User not logged in');
}

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::createInstance($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

try {
	$newname = $_POST['name'];
	ServiceData::updateName($sid, $newname);
	
	echo json_encode(array(
		'save' => 1,
		'name' => $newname,
	));
} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage(),
		'save' => 0,
	));
}
