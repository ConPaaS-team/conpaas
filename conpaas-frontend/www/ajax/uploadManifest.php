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
require_once("__init__.php");
require_module('db');
require_module('user');

try {
	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}

	$specs = "";
	if (is_uploaded_file($_FILES['specfile']['tmp_name'])) {
		$specs = file_get_contents($_FILES['specfile']['tmp_name']);
	} else if (isset($_POST['json'])) {
		$specs = $_POST['json'];
	} else {
		throw new Exception("Error reading the manifest");
	}

	$specs = preg_replace("/\n/", "", $specs);
	$specs = preg_replace("/\t/", "", $specs);

	$res = json_decode(HTTPS::post(Conf::DIRECTOR . '/upload_manifest',
		array( 'manifest' => $specs, 'thread' => 1 ), false, $_SESSION['uid']));

	if (!$res) {
		throw new Exception('The manifest has some errors in it');
	}

	if (property_exists($res, 'msg')) {
		throw new Exception($res->msg);
	}

	echo json_encode(array(
		'upload' => 1,
	));
} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}

?>
