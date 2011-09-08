<?php 

require_once('../__init__.php');
require_once('../UserData.php');
require_once('../ServiceData.php');
require_once('../ServiceFactory.php');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$uid           = $_SESSION['uid'];
$uinfo         = UserData::getUserById($uid);
$services_data = ServiceData::getServicesByUser($uid);

$instances = 0;
foreach ($services_data as $service_data) {
  $service = ServiceFactory::createInstance($service_data);
  $instances += $service->getNodesCount()+1;
}

echo json_encode(array(
		       'credit' => $uinfo['credit'],
		       'instances' => (string)$instances));

?>