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

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

try {
	$sid = $_GET['sid'];
	$service_data = ServiceData::getServiceById($sid);
	$service = ServiceFactory::create($service_data);

    if($service->getUID() !== $_SESSION['uid']) {
        throw new Exception('Not allowed');
    }

	$service->terminateService();
	echo json_encode(array(
		'terminate' => 1,
	));
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}