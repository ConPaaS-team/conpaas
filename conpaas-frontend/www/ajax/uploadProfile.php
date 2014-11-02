<?php

require_once('../__init__.php');
require_module('https');
require_module('application');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}


	

try {
	// $fileContent = file_get_contents($_FILES['profile']['tmp_name']);
	$filename = $_FILES['profile']['tmp_name'];
	//upload it to the application manager
	$aid = $_POST['aid'];
	$application_data = ApplicationData::getApplicationById($_SESSION['uid'], $aid);
	$application = new Application($application_data);

	$res = $application->upload_profile($filename);

	$res = $application->getProfilingInfo(false);
	$res = $res['pm'];

    print json_encode($res);
	

} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage()
	));
}

	


?>
