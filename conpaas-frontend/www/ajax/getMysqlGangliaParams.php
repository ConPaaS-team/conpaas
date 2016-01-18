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
	$json = $service->getGangliaParams();
	

} catch (Exception $e) {
	$json = 'Stats not available';
}
echo json_encode($json);


 ?>
