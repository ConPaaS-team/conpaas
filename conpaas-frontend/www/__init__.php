<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

session_set_cookie_params(60 * 60 * 24 * 15); // expires in 15 days
session_start();
date_default_timezone_set('Europe/Amsterdam');

class Conf {
        // Edit the CONF_DIR variable to point to the directory
        // containing your frontend's configuration files.
	const CONF_DIR = '/etc/conpaas';

	// Edit the HOST variable to contain the DNS name under 
	// which your front-end will be accessible
	const HOST = 'conpaas.yourdomain.com';

	/////////////////////////////////////////////////////////////////////
	// DO NOT EDIT BELOW THIS LINE UNLESS YOU KNOW WHAT YOU ARE DOING! //
	/////////////////////////////////////////////////////////////////////

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
