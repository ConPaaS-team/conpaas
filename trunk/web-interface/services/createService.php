<?php

require_once('__init__.php');
require_once('../DB.php');
require_once('../Service.php');
require_once('../ServiceFactory.php');
require_once('../ServiceData.php');

try {

	if ($_SERVER['REQUEST_METHOD'] != 'POST') {
		throw new Exception('Only calls with POST method accepted');
	}
	
	if (!array_key_exists('type', $_POST) || !array_key_exists('sw_version', $_POST)) {
		throw new Exception('Missing parameters');
	}
	
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}
	
	$type = $_POST['type'];
	$sw_version = $_POST['sw_version'];
	$default_name = $type.' service';
	$cloud = $_POST['cloud'];
	$uid = $_SESSION['uid'];
	
	$query = sprintf("INSERT INTO services ".
		"(name, type, cloud, state, creation_date, uid) VALUES ".
		"('%s', '%s', '%s', %d, now(), %d)",
		$default_name,
		$type,
		$cloud,
		Service::STATE_PREINIT,
		$uid
	);
	$res = mysql_query($query, DB::getConn());
	if ($res === false) {
		throw new DBException(DB::getConn());
	}
	
	/* get the service id */
	$sid = mysql_insert_id(DB::getConn());
	/* start the instance */
	$service_data = ServiceData::getServiceById($sid);
	$service = ServiceFactory::createInstance($service_data);
	$vmid = $service->getCloudInstance()->createManagerInstance();
	ServiceData::updateVmid($sid, $vmid);
	
	echo json_encode(array(
		'sid' => $sid,
		'create' => 1,
	));
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}