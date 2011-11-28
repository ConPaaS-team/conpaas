<?php 
  // Copyright (C) 2010-2011 Contrail consortium.
  //
  // This file is part of ConPaaS, an integrated runtime environment 
  // for elastic cloud applications.
  //
  // ConPaaS is free software: you can redistribute it and/or modify
  // it under the terms of the GNU General Public License as published by
  // the Free Software Foundation, either version 3 of the License, or
  // (at your option) any later version.
  //
  // ConPaaS is distributed in the hope that it will be useful,
  // but WITHOUT ANY WARRANTY; without even the implied warranty of
  // MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  // GNU General Public License for more details.
  //
  // You should have received a copy of the GNU General Public License
  // along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.

require_once('UserData.php');
require_once('ServiceData.php');

class Page {
	
	const UFILE = 'services/users.ini';
	
	protected $uid;
	protected $username;
	
	protected $browser;
	
	public static function redirect($toURL) {
		header('Location: '.$toURL);
		exit();
	}
	
	private function fetchBrowser() {
		$user_agent = $_SERVER['HTTP_USER_AGENT'];
		if (strpos($user_agent, 'Firefox') !== false) {
			$this->browser = 'firefox';
		} else if (strpos($user_agent, 'WebKit') != false) {
			$this->browser = 'webkit';
		} else {
			$this->browser = 'other';
		}
	}
	
	public function __construct() {
		if (isset($_SESSION['uid'])) {
			$this->uid = $_SESSION['uid'];
		} else {
			self::redirect('login.php');
		}
		$uinfo = UserData::getUserById($this->uid);
		if ($uinfo === false) {
			throw new Exception('User does not exist');
		}
		$this->username = $uinfo['username'];
		$this->user_credit = $uinfo['credit'];
		$this->instances = $uinfo['instances'];
		$this->fetchBrowser();
	}
	
	public function getUserCredit() {
	    return $this->user_credit;
	}
	
	public function getInstances() {
       	 $instances = 0;
	 $services_data = ServiceData::getServicesByUser($this->uid);

	 foreach ($services_data as $service_data) {
	   $service = ServiceFactory::createInstance($service_data);
	   $instances += $service->getNodesCount()+1;
	 }
	 return $instances;
	}
	
	public function getBrowserClass() {
		return $this->browser;
	}
	
	public function getUsername() {
		return $this->username;
	}
	
	public function getUID() {
		return $this->uid;
	}
	
	/* render functions */
	public function renderHeader() {
		return 
			'<div class="header">'.
  				'<a id="logo" href="index.php"></a>'.
  				'<div class="user">'.
  					$this->getUsername().' | '.
  					'<span id="user_instances_container">'.
  					    '<span id="user_instances">' .
  					        $this->getInstances() .
  					    '</span>'.
  					    ' active VMs'.
		                        '</span> |' .
		                        ' <span id="user_credit_container">'.
  					    '<span id="user_credit">'.
  					      $this->getUserCredit().
  					    '</span>'.
  					    ' credits'.
  					'</span> | <a href="http://www.conpaas.eu/?page_id=32" target="_blank">help</a> | '.
  					'<a href="javascript: void(0);" id="logout">logout</a>'.
  				'</div>'.
  				'<div class="clear"></div>'.
  			'</div>';
	}
	
}

?>