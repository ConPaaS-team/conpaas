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
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once('../__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('ui');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

try {
	$sampling_results = $service->fetchSamplingResults();
	for ($i = 0; $i < count($sampling_results); $i++) {
		$sampling = &$sampling_results[$i];
		$utc_ts = intval(intval($sampling['timestamp']) / 1000);
		$sampling['name'] = 'sampled '.
			TimeHelper::timeRelativeDescr($utc_ts).' ago';
	}
	echo json_encode($sampling_results);
} catch (Exception $e) {
	echo json_encode(array('error' => $e->getMessage()));
	exit();
}