<?php

require_once('DB.php');
require_once('logging.php');

class UserData {
    public static function createUser($username, $email, $fname, $lname, $affiliation, $passwd) {
        $query = sprintf("INSERT INTO users (username, email, fname, lname, affiliation, passwd, created) ".
    		"VALUES ('%s', '%s', '%s', '%s', '%s', '%s', now())",
    		mysql_escape_string($username),
    		mysql_escape_string($email),
    		mysql_escape_string($fname),
    		mysql_escape_string($lname),
    		mysql_escape_string($affiliation),
    		mysql_escape_string(md5($passwd)));
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
	
	public static function updateUserCredit($uid, $increment) {
	    try{
	      $conn = DB::getConn();
            if(mysql_query('BEGIN', $conn) === false) {
              throw new DBException($conn);
            }
            $query = sprintf("UPDATE users SET credit=credit+('%s') WHERE uid='%s'",
                mysql_escape_string($increment),
                mysql_escape_string($uid));
            $res = mysql_query($query, $conn);
            if ($res === false) {
                throw new DBException($conn);
            }
            if($increment < 0) {
                $query = sprintf("SELECT credit FROM users WHERE uid='%s'", $uid);
                $res = mysql_query($query, $conn);
                if ($res === false) {
                    throw new DBException($conn);
                }
        	    $entries = DB::fetchAssocAll($res);
        		if (count($entries) != 1) {
        			throw new DBException($conn);
        		}
                if ($entries[0]['credit'] < 0) {
                  mysql_query("ROLLBACK");
                  return false;
                }
            }
            if(mysql_query("COMMIT") === false) {
                throw new DBException($conn);
            }
            return true;
        } catch (DBException $e) {
            mysql_query('ROLLBACK', $conn);
            throw $e;
        }
	}
}

?>