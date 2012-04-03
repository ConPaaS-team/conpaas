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
			$user = UserData::getUserById($uid);
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