<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('logging');
require_module('application');
require_module('ui/application');

try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}
	$uid = $_SESSION['uid'];

	$applications_data = ApplicationData::getApplications($uid);
	$applicationsList = new ApplicationsListUI(array());
	foreach ($applications_data as $application_data) {
		$application = new Application($application_data);
		$applicationsList->addApplication($application);
	}
	$applications_data = $applicationsList->toArray();
	echo json_encode(array(
		'data' => $applications_data,
		'html' => $applicationsList->render()
	));
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array('error' => $e->getMessage()));
}
