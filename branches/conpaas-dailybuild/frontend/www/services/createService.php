<?php
  // Copyright (C) 2010-2011 Contrail consortium.
  //
  // This file is part of ConPaaS, an integrated runtime environment 
  // for elastic cloud applications.
  //
  // ConPaaS is free software: you can redistribute it and/or modify
  // it under the terms of the GNU General Public License as published by
  // the Free Software Foundation, either version 3 of the License, or
  // (at your option) any later version.
  //
  // ConPaaS is distributed in the hope that it will be useful,
  // but WITHOUT ANY WARRANTY; without even the implied warranty of
  // MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  // GNU General Public License for more details.
  //
  // You should have received a copy of the GNU General Public License
  // along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.

require_once('__init__.php');
require_once('../DB.php');
require_once('../Service.php');
require_once('../ServiceFactory.php');
require_once('../ServiceData.php');

try {

	if ($_SERVER['REQUEST_METHOD'] != 'POST') {
		throw new Exception('Only calls with POST method accepted');
	}
	
	if (!array_key_exists('type', $_POST) || !array_key_exists('sw_version', $_POST)) {
		throw new Exception('Missing parameters');
	}
	
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}
	
	$type = $_POST['type'];
	$sw_version = $_POST['sw_version'];
	$default_name = $type.' service';
	$cloud = $_POST['cloud'];
	$uid = $_SESSION['uid'];
	
	$sid = ServiceData::createService($default_name, $type, $cloud, $uid);
	if ($sid === false) {
	  throw new Exception("Not enough credit");
	}
	/* start the instance */
	$service_data = ServiceData::getServiceById($sid);
	$service = ServiceFactory::createInstance($service_data);
	$vmid = $service->getCloudInstance()->createManagerInstance();
	ServiceData::updateVmid($sid, $vmid);
	
	echo json_encode(array(
		'sid' => $sid,
		'create' => 1,
	));
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}