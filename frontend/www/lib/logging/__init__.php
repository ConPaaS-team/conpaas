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

class Logging {

	public static $logfile = null;
	
	public static function loadConf() {
	  $conf = parse_ini_file(Conf::CONF_DIR.'/main.ini', true);
	  if ($conf === false) {
	    throw new Exception('Could not read configuration file main.ini');
	  }
	  return $conf['main'];
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
	$conf = Logging::loadConf();
	Logging::$logfile = fopen($conf['logfile'], 'a');
}

function dlog($var) {
	Logging::log($var);
}