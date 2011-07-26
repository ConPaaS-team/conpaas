<?php 


require_once('../__init__.php');
require_once('../Service.php');
require_once('../ServiceData.php');
require_once('../ServiceFactory.php');

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::createInstance($service_data);

/*
 * HACK: PHP translates 'conf.max_limit' into 'conf_max_limit',
 * so we need to fix this before we send the request to the 
 * manager.
 */
$params = array();
foreach ($_POST as $key => $value) {
	if (strpos($key, 'phpconf') === 0) {
		$key = str_replace('phpconf_', 'phpconf.', $key);
	}
	$params[$key] = $value;
}

$response = $service->sendConfiguration($params);
echo $response;


?>
