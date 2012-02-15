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

require_module('db');
require_module('logging');

class UserData {
    public static function createUser($username, $email, $fname, $lname,
    		$affiliation, $passwd, $credit) {
        $query = sprintf("INSERT INTO users (username, email, fname, lname, affiliation, passwd, credit, created) ".
    		"VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', now())",
    		mysql_escape_string($username),
    		mysql_escape_string($email),
    		mysql_escape_string($fname),
    		mysql_escape_string($lname),
    		mysql_escape_string($affiliation),
    		mysql_escape_string(md5($passwd)),
    		mysql_escape_string($credit));
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