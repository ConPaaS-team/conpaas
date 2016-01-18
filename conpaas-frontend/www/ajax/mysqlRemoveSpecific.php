<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('__init__.php');
require_module('service');
require_module('service/factory');
require_module('ui/page');

try {
	$page = new Page(); // this will check the authentication
	$sid = $_GET['sid'];
	$ip= $_GET['ip'];
	$service_data = ServiceData::getServiceById($sid);
	$service = ServiceFactory::create($service_data);
	$json = $service->remove_specific_node($ip);
	if($service->getUID() !== $_SESSION['uid']) {
            throw new Exception('Not allowed');
        }

} catch (Exception $e) {
	$json = 'Elimination Error';
}
echo json_encode($json);
header("location: ../service.php?sid=".$sid); 

 ?>
