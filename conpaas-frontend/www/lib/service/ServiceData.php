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

require_module('https');

class ServiceData {

    public static function createService($default_name, $type, $cloud, $uid,
    		$initial_state) {
        $query = sprintf("INSERT INTO services ".
    		"(name, type, cloud, state, creation_date, uid) VALUES ".
    		"('%s', '%s', '%s', '%s', '%s', %d)",
    		mysql_escape_string($default_name),
    		mysql_escape_string($type),
    		mysql_escape_string($cloud),
    		mysql_escape_string($initial_state),
    		date("Y-m-d H:i:s"),
    		mysql_escape_string($uid)
    	);
    	$res = mysql_query($query, DB::getConn());
    	if ($res === false) {
    		throw new DBException(DB::getConn());
    	}

    	/* get the service id */
    	$sid = mysql_insert_id(DB::getConn());
    	return $sid;
    }

	public static function getServicesByUser($uid) {
       $res = HTTPS::post(Conf::DIRECTOR . '/list', array(), false, $uid);

       $services = array();
       foreach(json_decode($res) as $service) {
           $service = (array)$service;
           $service['uid'] = $service['user_id'];
           $service['creation_date'] = $service['created'];
           array_push($services, $service);
       }
       return $services;
	}

	public static function getServiceById($sid) {
        $services = ServiceData::getServicesByUser($_SESSION['uid']);
        foreach ($services as $service) {
            if ($service['sid'] == $sid) {
                return $service;
            }
        }
        throw new Exception('Service does not exist');
	}

	public static function updateVmid($sid, $vmid) {
		$query = sprintf("UPDATE services SET vmid='%s' WHERE sid=%d",
			mysql_escape_string($vmid), mysql_escape_string($sid));
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
	}

	public static function updateName($sid, $name) {
        $res = HTTPS::post(Conf::DIRECTOR . '/rename/'.$sid, 
            array('name' => $name), false, $_SESSION['uid']);

		if (json_decode($res) !== true) {
			throw new Exception('Cannot rename service');
		}
	}

	public static function updateState($sid, $state) {
	}

	public static function getAvailableCds($uid) {
		$query = sprintf("SELECT * FROM services WHERE type='cds'"
			." and state='RUNNING'"
			." and cloud='ec2'"
			." and (uid = 1 or uid = %d)",
			mysql_escape_string($uid));
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
		return DB::fetchAssocAll($res);
	}

	public static function getCdsByAddress($address) {
		$query = sprintf("SELECT * FROM services WHERE type='cds'"
			." and manager like '%s'",
			'%'.mysql_escape_string($address).'%');
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
		$entries = DB::fetchAssocAll($res);
		return $entries[0];
	}
}

?>
