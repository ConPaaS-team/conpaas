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
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('http');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

function unlink_paths($paths) {
	foreach ($paths as $file => $path) {
		unlink($path);
	}
}

$paths = array();
foreach (array('botFile', 'clusterFile') as $file) {
	$path = '/tmp/'.$_FILES[$file]['name'];
	if (move_uploaded_file($_FILES[$file]['tmp_name'], $path) === false) {
		echo json_encode(array(
			'error' => 'could not move uploaded file '.$file
		));
		unlink_paths($paths);
		exit();
	}
	// build the cURL parameter
	$paths[$file] = '@'.$path;
}
$params = array_merge($_POST, $paths);
try {
	$params['method'] = 'start_sampling';
	$json_response = HTTP::post($service->getManager(), $params);
	$response = json_decode($json_response, true);
	if (array_key_exists('result', $response)) {
		$response = $response['result'];
	}
	echo json_encode($response);
} catch (Exception $e) {
	echo json_encode(array('error' => $e->getMessage()));
}
unlink_paths($paths);
