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

require_module('user');
require_module('ui');

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

	public function isLoginPage() {
		return strpos($_SERVER['SCRIPT_NAME'], 'login.php') !== false;
	}

	public function __construct() {
		$this->fetchBrowser();
		if (isset($_SESSION['uid'])) {
			$this->uid = $_SESSION['uid'];
			if ($this->isLoginPage()) {
				self::redirect('index.php');
			}
		} else {
			if (!$this->isLoginPage()) {
				self::redirect('login.php');
			}
			return;
		}
		$uinfo = UserData::getUserById($this->uid);
		if ($uinfo === false) {
			throw new Exception('User does not exist');
		}
		$this->username = $uinfo['username'];
		$this->user_credit = $uinfo['credit'];
	}

	public function getUserCredit() {
	    return $this->user_credit;
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

	public function renderIcon() {
		return '<link rel="shortcut icon" href="images/conpaas.ico">';
	}

	public function renderHeader() {
		return
			'<div class="header">'.
  				'<a id="logo" href="index.php"></a>'.
  				'<div class="user">'.
  					'<div class="logout">'.
  						'<a href="javascript: void(0);" id="logout">logout</a>'.
  					'</div>'.
  					'<div class="usercredit" id="user_credit_container" title="credits">'.
  						'<span id="user_credit">'.
  					      $this->getUserCredit().
  					    '</span>'.
  					'</div>'.
					'<div class="username">'
						.$this->getUsername()
					.'</div> '.
  				'</div>'.
  				'<div class="clear"></div>'.
  			'</div>';
	}

	public function renderFooter() {
		return
			'<div class="footer">'.
				'&copy;2011 <a href="http://contrail-project.eu/">Contrail</a> - ConPaaS is the PaaS component of <a href="http://contrail-project.eu/">Contrail</a>'.
			'</div>';
	}

}

?>