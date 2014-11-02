<?php

require_once('../__init__.php');
require_module('application');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}


	

try {

	$service = $_POST['service'];
	if ($service == 'echo'){
		$fileContent = file_get_contents($_FILES['slo']['tmp_name']);
		//upload it to the application manager
		echo $fileContent;
	}else{
		$aid = $_POST['aid'];
		$application_data = ApplicationData::getApplicationById($_SESSION['uid'], $aid);
		$application = new Application($application_data);

		$slocontent = $_POST['slo'];
		$slopath = "/tmp/slo.json";
		$slofile = fopen($slopath, "w");
		fwrite($slofile, $slocontent);
		fclose($slofile);
		
		$res = $application->upload_slo($slopath);
		
		// print $res
		print json_encode($res);

		// echo json_encode(array(
		//    'lesh' => $aid
		// ));
	}

} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage()
	));
}




?>
