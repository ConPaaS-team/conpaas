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

class DB {

	private static $conn = null;

	private static function loadConfiguration() {
		$conf = parse_ini_file(Conf::CONF_DIR.'/db.ini', true);
		if ($conf === false) {
			throw new Exception('Could not read db configuration file db.ini');
		}
		return $conf['mysql'];
	}
	
	public static function getConn() {
		if (self::$conn === null) {
			$conf = self::loadConfiguration();
			self::$conn = mysql_connect($conf['server'], $conf['user'], 
				$conf['pass']);
			if (self::$conn === FALSE) {
				throw new Exception('Could not connect to the DB');
			}
			mysql_select_db($conf['db'], self::$conn);
			mysql_set_charset('utf8', self::$conn);
		}
		return self::$conn;
	}

	public static function fetchAssocAll($res) {
		$rows = array();
		while ($row = mysql_fetch_assoc($res)) {
			$rows[] = $row;
		}
		return $rows;
	}
}

class DBException extends Exception {

	public function __construct($conn) {
		parent::__construct(mysql_error($conn), mysql_errno($conn));
	}
}
