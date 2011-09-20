<?php 


require_once('../__init__.php');
require_once('../Service.php');
require_once('../ServiceData.php');
require_once('../ServiceFactory.php');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::createInstance($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

/*
 * HACK: PHP translates 'conf.max_limit' into 'conf_max_limit',
 * so we need to fix this before we send the request to the 
 * manager.
 */

$response = $service->sendConfiguration($_POST);
echo $response;


?>
