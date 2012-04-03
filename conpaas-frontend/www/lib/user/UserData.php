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