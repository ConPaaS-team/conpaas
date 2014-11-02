<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('__init__.php');
require_module('https');
require_module('application');
// require_module('service');
// require_module('service/factory');

try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}

	if (!isset($_SESSION['aid'])) {
		throw new Exception('The aid is not in the session');
	}

	$aid = $_GET['aid'];
	$application_data = ApplicationData::getApplicationById($_SESSION['uid'], $aid);
	$application = new Application($application_data);
	
	$res = array();
	if($application->manager == ''){
		$res['ready'] = false;
		$res['status'] = 'Starting Application Manager';
	}else
	{
		if(isset($_GET['format']) && $_GET['format'] == 'file'){
			header("Content-type: application/json");
			header('Content-Disposition:attachment;filename="' . 'profile.json' . '"');
			$info = $application->getProfilingInfo(true);
			$res = $info['pm'];
		}else{
			$res['ready'] = true;
			$info = $application->getProfilingInfo(false);
			$res['profile'] = $info;
		}
		

	}

	

	print json_encode($res);
    // print json_encode($application);
	// $info = $application->getProfilingInfo();
	// $res = array('profiling_info' => $info);
	// print json_encode($res);
	
} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}
?>
