<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('user');

class Logging {

	public static $logfile = null;

	public static function loadConf() {
	  $conf = parse_ini_file(Conf::CONF_DIR.'/main.ini', true);
	  if ($conf === false) {
	    throw new Exception('Could not read configuration file main.ini');
	  }
	  return $conf['main'];
	}

	public static function getLogFilename() {
		$conf = self::loadConf();
		$logFilename = $conf['logfile'];
		if (strpos($logFilename, '%u') !== false && isset($_SESSION['uid'])) {
			$uid = $_SESSION['uid'];
			$user = UserData::getUserByName($_SESSION['username']);
			if ($user !== false) {
				$username = $user['username'];
				$logFilename = str_replace('%u', $username, $logFilename);
			}
		}
		return $logFilename;
	}

	public static function log($var) {
		if (!Logging::$logfile) {
			return;
		}
        fwrite(Logging::$logfile, date('d-m-Y h:i:s').' '.print_r($var, true)
        	."\n");
	}
}

if (Logging::$logfile === null) {
	// initialize
	Logging::$logfile = fopen(Logging::getLogFilename(), 'a');
}

function dlog($var) {
	Logging::log($var);
}
