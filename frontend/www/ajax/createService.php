<?php
/*
 * Copyright (C) 2010-2011 Contrail consortium.                                                                                                                       
 *
 * This file is part of ConPaaS, an integrated runtime environment                                                                                                    
 * for elastic cloud applications.                                                                                                                                    
 *                                                                                                                                                                    
 * ConPaaS is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by                                                                                               
 * the Free Software Foundation, either version 3 of the License, or                                                                                                  
 * (at your option) any later version.
 * ConPaaS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of                                                                                                     
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                                                                                      
 * GNU General Public License for more details.                                                                                                                       
 *
 * You should have received a copy of the GNU General Public License                                                                                                  
 * along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once('__init__.php');
require_module('db');
require_module('user');
require_module('service');
require_module('service/factory');

try {

	if ($_SERVER['REQUEST_METHOD'] != 'POST') {
		throw new Exception('Only calls with POST method accepted');
	}
	
	if (!array_key_exists('type', $_POST)) {
		throw new Exception('Missing parameters');
	}
	
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}
	
	$type = $_POST['type'];
	$default_name = 'New '.ucfirst($type).' Service';
	$cloud = $_POST['cloud'];
	$uid = $_SESSION['uid'];

    if (UserData::updateUserCredit($uid, -1) === false) {
	  	throw new Exception("Not enough credit");
    }
	$sid = ServiceData::createService($default_name, $type, $cloud, $uid, 
		Service::STATE_PREINIT);
	/* start the instance */
	$service_data = ServiceData::getServiceById($sid);
	$service = ServiceFactory::create($service_data);
	$vmid = $service->getManagerInstance()->run();
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