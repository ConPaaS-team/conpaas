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

require_once('../__init__.php');
require_module('service');
require_module('service/factory');
require_module('ui/service');

try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}
	$uid = $_SESSION['uid'];

	$services_data = ServiceData::getServicesByUser($uid);
	$servicesList = new ServicesListUI(array());
	foreach ($services_data as $service_data) {
		$service = ServiceFactory::create($service_data);
		$servicesList->addService($service);
		if ($service->needsPolling()) {
			$service->checkManagerInstance();
		}
	}
	$services_data = $servicesList->toArray();
	echo json_encode(array(
		'data' => $services_data,
		'html' => $servicesList->render()
	));
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array('error' => $e->getMessage()));
}
