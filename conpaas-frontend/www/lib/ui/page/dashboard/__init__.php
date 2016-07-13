<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/page');

class Dashboard extends Page {

	public function __construct() {
		parent::__construct();
		$this->addJS('js/service.js');
		$this->addJS('js/dashboard.js');
	}

	public function renderPageHeader() {
		return
			'<div class="menu">'
				.'<a class="button" id="newapp" href="#">'
					.'<img src="images/service-plus.png" /> create new application'
				.'</a>'
				.'<a class="button" href="manifest.php">'
					.'<img src="images/active.png" /> deploy application from manifest'
				.'</>'
  				.'<a class="button" href="ajax/getCertificate.php">'
  					.'<img src="images/green-down.png" /> download certificate'
  				.'</a>'
  				.'<a class="button" href="resources.php">'
  					.'<img src="images/server-icon.png" /> resources'
  				.'</a>'
			.'</div>'
			.'<div class="clear"></div>';
	}

	public function renderContent() {

	}
}
