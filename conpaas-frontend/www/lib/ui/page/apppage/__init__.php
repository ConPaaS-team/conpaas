<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/page');

class Apppage extends Page {

	public function __construct() {
		parent::__construct();
		$this->addJS('js/servicepage.js');
		$this->addJS('js/application.js');
	}

	public function renderPageHeader() {
		return
			'<div class="menu">'
				.'<a class="button" id="newapp" href="#">'
					.'<img src="images/service-plus.png" /> create new application'
				.'</a>'
				.'<a class="button" href="manifest.php">'
					.' deploy ready-made application'
				.'</>'
  				.'<a class="button" href="ajax/getCertificate.php">'
  					.' download certificate'
  				.'</a>'
			.'</div>'
			.'<div class="clear"></div>';
	}

	public function renderContent() {

	}
}
