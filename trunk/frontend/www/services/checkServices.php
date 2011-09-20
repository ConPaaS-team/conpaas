<?php 

require_once('../__init__.php');
require_once('../ServiceData.php');
require_once('../ServicesListUI.php');
require_once('../ServiceFactory.php');

try {
	
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}
	
	$uid = $_SESSION['uid'];
	
	$services_data = ServiceData::getServicesByUser($uid);
	$servicesList = new ServicesListUI(array());
	foreach ($services_data as $service_data) {
		$service = ServiceFactory::createInstance($service_data);
		$servicesList->addService($service);
		if ($service->needsPolling()) {
			$service->checkManagerInstance();
		}
	}
	echo $servicesList->render();
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo '<div class="error">'.$e->getMessage().'</div>';
}
