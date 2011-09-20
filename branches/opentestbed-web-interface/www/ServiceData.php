<?php 

require_once('DB.php');
require_once('UserData.php');
require_once('Service.php');

class ServiceData {
	
    public static function createService($default_name, $type, $cloud, $uid) {
        if (UserData::updateUserCredit($uid, -1) === false) {
          /* not enough credit */
          return false;
        }
        $query = sprintf("INSERT INTO services ".
    		"(name, type, cloud, state, creation_date, uid) VALUES ".
    		"('%s', '%s', '%s', %d, now(), %d)",
    		mysql_escape_string($default_name),
    		mysql_escape_string($type),
    		mysql_escape_string($cloud),
    		mysql_escape_string(Service::STATE_PREINIT),
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
		$query = sprintf("SELECT * FROM services WHERE uid='%s' ".
			" ORDER BY sid DESC",
			mysql_escape_string($uid));
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
		return DB::fetchAssocAll($res);
	}
	
	public static function getServiceById($sid) {
		$query = sprintf("SELECT * FROM services WHERE sid='%s' LIMIT 1",
			mysql_escape_string($sid));
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
		$entries = DB::fetchAssocAll($res);
		if (count($entries) != 1) {
			throw new Exception('Service does not exist');
		}
		return $entries[0];
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
		$query = sprintf("UPDATE services SET name='%s' WHERE sid=%d",
			mysql_escape_string($name), 
			mysql_escape_string($sid)); 
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
	}
	
	
	public static function updateManagerAddress($sid, $manager) {
		$query = sprintf("UPDATE services SET manager='%s', state=%d ".
			" WHERE sid=%d",
			mysql_escape_string($manager),
			mysql_escape_string(Service::STATE_INIT),
			mysql_escape_string($sid)); 
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
	}
	
	public static function updateState($sid, $state) {
		$query = sprintf("UPDATE services SET state=%d WHERE sid=%d",
			mysql_escape_string($state),
			mysql_escape_string($sid)); 
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
	}
	
	public static function deleteService($sid) {
		$query = sprintf("DELETE FROM services WHERE sid=%d",
		    mysql_escape_string($sid));
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
	}
	
}

?>