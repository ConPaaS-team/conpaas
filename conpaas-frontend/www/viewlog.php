<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('__init__.php');
require_module('service');
require_module('service/factory');
require_module('ui/page');
require_module('application');

try {
	$page = new Page(); // this will check the authentication
	if (isset($_GET['sid'])) {
		$sid = $_GET['sid'];
		$service_data = ServiceData::getServiceById($sid);
		$service = ServiceFactory::create($service_data);

		if (isset($_GET['agentId'])) {
			unset($_GET['sid']);
			$log = $service->fetchAgentLog($_GET);
		} else {
			$log = $service->fetchLog();
		}
	} else {
		$applications_data = ApplicationData::getApplications($_SESSION['uid'], $_SESSION['aid']);
		if (count($applications_data) > 0) {
			$application = new Application($applications_data[0]);
			$log = $application->fetchLog();
		}
	}
} catch (Exception $e) {
	$log = 'Log information not available';
}
?>

<pre><?php echo $log; ?></pre>
