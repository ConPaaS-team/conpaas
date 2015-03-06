<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('service');
require_module('service/factory');
require_module('ui/service');
require_module('ui/page');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$sid = $_GET['sid'];
$target = $_GET['target'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

$page = PageFactory::create($service);

switch ($target) {
	case 'versions':
		echo $page->renderCodeVersions();
		break;
	case 'instances':
		echo $page->renderInstances();
		break;
	case 'volumes':
		echo $page->renderVolumeList();
		break;
	case 'xtreemfs_volumes':
		$volumes = $service->listVolumes();
		$volumeList = $page->renderVolumeList($volumes);
		$volumeSelector = $page->renderVolumeSelectorOptions($volumes);
		$response = array("volumeList"=>$volumeList,
		                  "volumeSelector"=>$volumeSelector);
		echo json_encode($response);
		break;
	default:
		echo "error: unknow target $target for rendering";
}


?>
