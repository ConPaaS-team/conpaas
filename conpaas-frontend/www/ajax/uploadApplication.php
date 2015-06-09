<?php

require_once("__init__.php");
require_module('db');
require_module('user');
require_module('application');

try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}

	
	
	$app = "";
	
	if (is_uploaded_file($_FILES['appfile']['tmp_name'])) {
		$app = $_FILES['appfile']['tmp_name'];
	
	} else {
		throw new Exception("Error reading the application");
	}

	$aid = $_POST['aid'];
	$application_data = ApplicationData::getApplicationById($_SESSION['uid'], $aid);
	$application = new Application($application_data);

	$res = $application->upload_application($app);
		
		
	echo json_encode($res);
	
	// $res = json_decode(HTTPS::post(Conf::DIRECTOR . '/upload_manifest',
	//  	// array( 'manifest' => $man, 'app_tar' => $app, 'thread' => 1 ), false, $_SESSION['uid']));
	//  	array( 'manifest' => $man, 'app_tar' => $app, 'thread' => 1 ), false, $_SESSION['uid']));

	// if (!$res) {
	// 	throw new Exception('The manifest has some errors in it');
	// }

	// if (property_exists($res, 'msg')) {
	// 	throw new Exception($res->msg);
	// }

	// echo json_encode(array(
	// 	'upload' => 1,
	// 	'appid' => $res->appid,
	// ));
	
	
} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}

?>
