<?php 

require_once('DB.php');
require_once('Service.php');

class ServiceData {
	
	public static function getServicesByUser($uid) {
		$query = sprintf("SELECT * FROM services WHERE uid='%s' ".
			" ORDER BY sid DESC",
			$uid);
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
		return DB::fetchAssocAll($res);
	}
	
	public static function getServiceById($sid) {
		$query = sprintf("SELECT * FROM services WHERE sid='%s' LIMIT 1",
			$sid);
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
			$vmid, $sid); 
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
	}
	
	public static function updateName($sid, $name) {
		$query = sprintf("UPDATE services SET name='%s' WHERE sid=%d",
			mysql_escape_string($name), 
			$sid); 
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
	}
	
	
	public static function updateManagerAddress($sid, $manager) {
		$query = sprintf("UPDATE services SET manager='%s', state=%d ".
			" WHERE sid=%d",
			$manager, Service::STATE_INIT, $sid); 
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
	}
	
	public static function updateState($sid, $state) {
		$query = sprintf("UPDATE services SET state=%d WHERE sid=%d",
			$state, $sid); 
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
	}
	
	public static function deleteService($sid) {
		$query = sprintf("DELETE FROM services WHERE sid=%d", $sid);
		$res = mysql_query($query, DB::getConn());
		if ($res === false) {
			throw new DBException(DB::getConn());
		}
	}
	
}

?>