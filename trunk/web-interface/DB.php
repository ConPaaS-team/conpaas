<?php

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
