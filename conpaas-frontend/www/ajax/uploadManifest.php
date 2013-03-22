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
include_once("../__init__.php");
require_module('db');

try {
	if ($_FILES['specfile']['error'] != UPLOAD_ERR_OK ||
	    ! is_uploaded_file($_FILES['specfile']['tmp_name'])) {
		throw new Exception("Error reading the file");
	}

	$specs = file_get_contents($_FILES['specfile']['tmp_name']);
	$specs = preg_replace("/\n/", "", $specs);
	$specs = preg_replace("/\t/", "", $specs);

	echo json_encode(array('result' => $specs));
} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}

?>
