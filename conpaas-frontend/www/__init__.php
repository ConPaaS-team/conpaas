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

session_set_cookie_params(60 * 60 * 24 * 15); // expires in 15 days
session_start();
date_default_timezone_set('Europe/Amsterdam');

class Conf {

	const CONF_DIR = '/home/vuadriana/conpaas_v2/conf';
	const HOST = 'cumulus.zib.de';
	public static $ROOT_DIR = '';

	public static function getFrontendURL() {
		$page_url = 'http';
		if (isset($_SERVER['HTTPS']) && ($_SERVER['HTTPS'] == "on" )) {
			$page_url .= "s";
		}
		$page_url .= "://".self::HOST;
		if ($_SERVER["SERVER_PORT"] != "80") {
			$page_url .= ":".$_SERVER["SERVER_PORT"];
		}
		$r_uri = $_SERVER["REQUEST_URI"];

		// Note: the page url looks like:
		//       http://domainname.org/path/to/frontend/ajax/create.php
		//       so we also have to strip /ajax/create.php to
		//       obtain the path to frontend.
		// Attention!! If the directory structure of the frontend changes,
		// this code must also be changed
		$pos = strrpos($r_uri, "/ajax/");
		$page_url = $page_url.substr($r_uri, 0, $pos);

		return $page_url;
	}
}

Conf::$ROOT_DIR = dirname(__FILE__);

function require_module($name) {
	$lib = Conf::$ROOT_DIR.'/lib';
	// first check the module
	$module_dir = $lib.'/'.$name;
	if (!is_dir($module_dir)) {
		throw new Exception('Module '.$name.' cannot be found: directory '.
			$module_dir.' doesn\'t exist');
	}
	if (!is_file($module_dir.'/__init__.php')) {
		throw new Exception('Module '.$name.' doesn\'t have __init__.php file');
	}
	require_once($module_dir.'/__init__.php');
}

?>
