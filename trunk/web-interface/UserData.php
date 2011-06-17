<?php

require_once('DB.php');

class UserData {
	
	public static function getUserByName($username) {
		$query = sprintf("SELECT * FROM users WHERE username='%s'", $username);
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
		$entries = DB::fetchAssocAll($res); 
		if (count($entries) != 1) {
			return false;
		}
		return $entries[0];
	}
	
	public static function getUserById($uid) {
		$query = sprintf("SELECT * FROM users WHERE uid='%s'", $uid);
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
		$entries = DB::fetchAssocAll($res); 
		if (count($entries) != 1) {
			return false;
		}
		return $entries[0];
	}
}

?>