<?php 

require_once('../__init__.php');
require_once('../ServiceData.php');
require_once('../ServiceFactory.php');

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::createInstance($service_data);
if ($service->needsPolling()) {
	$update = $service->checkManagerInstance();
	if ($update) {
		$service_data = ServiceData::getServiceById($sid);
	}
}

echo json_encode($service_data);

?>