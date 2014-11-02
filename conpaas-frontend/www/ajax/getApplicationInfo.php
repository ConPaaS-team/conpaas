<?php

require_once('../__init__.php');
require_module('application');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

try {

	$aid = $_GET['aid'];
	$application_data = ApplicationData::getApplicationById($_SESSION['uid'], $aid);
	$application = new Application($application_data);

	
	$res = $application->infoapp();
	print json_encode($res);	

} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage()
	));
}




?>
