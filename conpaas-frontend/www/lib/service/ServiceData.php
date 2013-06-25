<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



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

	public static function getServicesByUser($uid, $aid) {
       $res = HTTPS::post(Conf::DIRECTOR . '/list/' . $aid, array(), false, $uid);

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
        $services = ServiceData::getServicesByUser($_SESSION['uid'], $_SESSION['aid']);
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
