<?php

require_once('DB.php');

class UserData {
    public static function createUser($username) {
        $query = sprintf("INSERT INTO users (username, created) ".
    		"VALUES ('%s', now())",
    		mysql_escape_string($username));
    	$res = mysql_query($query, DB::getConn());
    	if ($res === false) {
    		throw new DBException(DB::getConn());
    	}
    	$uid = mysql_insert_id(DB::getConn());
    	return $uid;
    }
    
	public static function getUserByName($username) {
		$query = sprintf("SELECT * FROM users WHERE username='%s'", mysql_escape_string($username));
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
		$query = sprintf("SELECT * FROM users WHERE uid='%s'", mysql_escape_string($uid));
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