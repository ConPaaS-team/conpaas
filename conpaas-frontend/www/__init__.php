<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



session_set_cookie_params(60 * 60 * 24 * 15); // expires in 15 days
session_start();
date_default_timezone_set('Europe/Amsterdam');

require_once('config.php');

class Conf {
	const CONF_DIR = CONPAAS_CONF_DIR;
	const HOST = CONPAAS_HOST;
	const DIRECTOR = DIRECTOR_URL;

	/*
	 * time, in seconds, elapsed since the creation of a service, after which
	 * that service is turned to ERROR state due to a prolongue unreachable INIT
	 * state, typical for a service that failed to start properly.
	 */
	const FAILOUT_TIME = 600; // 10 minutes

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
