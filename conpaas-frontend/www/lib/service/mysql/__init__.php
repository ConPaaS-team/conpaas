<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('cloud');
require_module('https');
require_module('service');
require_module('ui/instance/mysql');

class MySQLService extends Service {

	public function __construct($data, $manager) {
		parent::__construct($data, $manager);
	}

	

	public function sendConfiguration($params) {
		// we ignore this for now
		return '{}';
	}

	public function fetchHighLevelMonitoringInfo() {
		return false;
	}

	public function getInstanceRoles() {
		return array('nodes', 'glb_nodes');
	}

	public function createInstanceUI($node) {
		$info = $this->getNodeInfo($node);
		return new MySQLInstance($info);
	}

	public function needsPasswordReset() {
		$flag = 'must_reset_passwd_for_aid'.$_SESSION['aid'].'_sid'.$this->sid;
		return
			isset($_SESSION[$flag]);
	}

	public function setPassword($user, $password) {
		$resp = $this->managerRequest('post', 'set_password', array(
			'user' => $user,
			'password' => $password
		));
		$flag = 'must_reset_passwd_for_aid'.$_SESSION['aid'].'_sid'.$this->sid;
		unset($_SESSION[$flag]);
		return $resp;
	}

	public function getMasterAddr() {
                $list=$this->nodesLists;
		if(count($list['glb_nodes'])>0){
			$accessnode=$this->getNodeInfo($list['glb_nodes'][0]);
			$port='8010';
		}
	        else{
                        $accessnode=$this->getNodeInfo($this->nodesLists['nodes'][0]);
			$port='3306';
		}
                return array('ip' =>$accessnode['ip'] ,'port' => $port);
        }
	/*public function getMasterAddr() {
		$master_node = $this->getNodeInfo($this->nodesLists['nodes'][0]);
		return $master_node['ip'];
	}
*/
	public function getAccessLocation() {
		 $master_addr=$this->getMasterAddr();
		 return $master_addr['ip'].':'.$master_addr['port'];
	}

	public function getUsers() {
		return array('mysqldb');
	}

	public function loadFile($file) {
		return HTTPS::post($this->getManager(), array(
			'method' => 'load_dump',
			'mysqldump_file' => '@'.$file,
			'service_id' => $this->getSID()
			));
	}

	public function getCPU(){
			$json_info = $this->managerRequest('get', 'get_service_performance',array() );
                	$info = json_decode($json_info, true);
                if ($info == null) {
                        return false;
                }
		//print_r($info);
               return $info[ 'result' ]['throughput'];//var_export($info, true);
        }
	public function getMeanLoad(){
        $json_info = $this->managerRequest('get', 'getMeanLoad',array() );
        $info = json_decode($json_info, true);
        if ($info == null) 
            return false;
        return $info['result']['meanLoad'];
    }

	public function getMySqlStats(){
        $json_info = $this->managerRequest('get', 'getMeanLoad',array() );
        $info = json_decode($json_info, true);
        if ($info == null) {
            return false;
        }            
       return $info;
    }

	public function getGangliaParams(){
        $json_info = $this->managerRequest('get', 'getGangliaParams',array() );
        $info = json_decode($json_info, true);
        if ($info == null) {
            return false;
            }

       return $info;
	}


	public function remove_specific_node($ip){
        $json_info = $this->managerRequest('get', 'remove_specific_nodes',array('ip' => $ip) );
        $info = json_decode($json_info, true);
        if ($info == null) {
            return false;
        }

       return $info;
    }

}
?>
