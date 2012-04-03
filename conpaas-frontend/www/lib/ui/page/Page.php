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

	protected $uid;
	protected $user_credit;
	protected $username;
	protected $browser;
	protected $jsFiles = array('js/jquery-1.5.js', 'js/conpaas.js');

	public function __construct() {
		$this->fetchBrowser();
		if (isset($_SESSION['uid'])) {
			$this->uid = $_SESSION['uid'];
			if ($this->isLoginPage()) {
				self::redirect('index.php');
			}
		} else {
			// not logged in
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

	protected function addJS($url) {
		$this->jsFiles []= $url;
	}

	public static function redirect($toURL) {
		header('Location: '.$toURL);
		exit();
	}

	public function fetchBrowser() {
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

	public function renderDoctype() {
		return '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"'
			.' "http://www.w3.org/TR/html4/loose.dtd">';
	}

	public function renderContentType() {
		return '<meta http-equiv="Content-Type" content="text/html;'
			.' charset=utf-8" />';
	}

	public static function renderCSSLink($url) {
		return '<link type="text/css" rel="stylesheet" href="'.$url.'" />';
	}

	public static function renderScriptLink($url) {
		return '<script src="'.$url.'"></script>';
	}

	public function renderHeaderCSS() {
		return self::renderCSSLink('conpaas.css');
	}

	public function renderJSLoad() {
		$scripts = '';
		foreach ($this->jsFiles as $jsFile) {
			$scripts .= self::renderScriptLink($jsFile);
		}
		return $scripts;
	}

	public function renderTitle() {
		return '<title>ConPaaS - management interface</title>';
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

	public function renderPageStatus() {
		return
			'<div id="pgstat">'
			.'<div id="pgstatInfo" style="display: none;">'
				.'<img src="images/info.png" style="margin-right: 5px;"/>'
				.'<span id="pgstatInfoText">service is starting</span>'
				.'</div>'
			.'<div id="pgstatError" style="display: none;">'
				.'<img src="images/error.png" style="vertical-align: middle; margin-right: 5px;"/>'
				.'<span id="pgstatErrorName">service error</span>'
				.'<a id="pgstatErrorDetails" href="javascript: void(0);">'
					.'<img src="images/link_s.png" />details'
				.'</a>'
			.'</div>'
			.'<div id="pgstatLoading" style="display: none;">'
				.'<span id="pgstatLoadingText">creating service...</span>'
				.'<img class="loading" src="images/icon_loading.gif" style="vertical-align: middle;" /> '
			.'</div>'
			.'<div id="pgstatTimer" style="display: none;">'
				.'<img src="images/refresh.png" /> recheck in <i id="pgstatTimerSeconds">6</i> seconds </div>'
			.'<div class="clear"></div>'
			.'</div>';
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
  			'</div>'.
			$this->renderPageStatus();
	}

	public function renderFooter() {
		return
			'<div class="footer">'.
				'&copy;2010-2012 <a href="http://contrail-project.eu/">Contrail</a> - ConPaaS is the PaaS component of <a href="http://contrail-project.eu/">Contrail</a>'.
			'</div>';
	}

	public function generateJSGetParams() {
		return
			'<script>var GET_PARAMS = '.json_encode($_GET, JSON_HEX_TAG).';'
			.'</script>';
	}
}

?>