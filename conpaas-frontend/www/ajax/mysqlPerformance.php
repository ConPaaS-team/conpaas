<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('__init__.php');
require_module('service');
require_module('service/factory');
require_module('ui/page');

try {
	$page = new Page(); // this will check the authentication
	$sid = $_GET['sid'];
	$service_data = ServiceData::getServiceById($sid);
	$service = ServiceFactory::create($service_data);
	$json = $service-> getMeanLoad();
 	$load = json_decode($json, true);
 	$load['result']['meanLoad'];
} catch (Exception $e) {
	$load = 'Load not available';
}
?>

<?php  echo $load; ?>
