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

switch ($target) {
	case 'versions':
		$page = PageFactory::create($service);
		echo $page->renderCodeVersions();
		break;
	case 'instances':
		$page = PageFactory::create($service);
		echo $page->renderInstances();
		break;
	case 'volumes':
		$page = PageFactory::create($service);
		echo $page->renderVolumeList();
		break;
	case 'generic_script_status':
		$scriptStatusUIArray = $service->createScriptStatusUI();
		echo json_encode($scriptStatusUIArray);
		break;
	case 'xtreemfs_volumes':
		$page = PageFactory::create($service);
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
