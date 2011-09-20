<?php 

require_once('../__init__.php');
require_once('../Service.php');
require_once('../ServicePage.php');
require_once('../Version.php');
require_once('../ServiceData.php');
require_once('../ServiceFactory.php');

if (!isset($_SESSION['uid'])) {
    throw new Exception('User not logged in');
}

$sid = $_GET['sid'];
$target = $_GET['target'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::createInstance($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

switch ($target) {
	case 'versions':
		$page = new ServicePage($service);
		echo $page->renderVersions();
		break;
	case 'instances':
		$page = new ServicePage($service);
		echo $page->renderInstances();
		break;
	default:
		echo "error: unknow target $target for rendering";
}


?>