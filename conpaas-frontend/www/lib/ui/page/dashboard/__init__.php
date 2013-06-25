<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/page');

class Dashboard extends Page {

	public function __construct() {
		parent::__construct();
		$this->addJS('js/servicepage.js');
		$this->addJS('js/services.js');
	}

	public function renderPageHeader() {
		return
			'<div class="menu">'
  				.'<a class="button" href="create.php">'
  					.'<img src="images/service-plus.png" /> create new service'
  				.'</a>'
  			.'</div>'
  			.'<div class="clear"></div>';
	}

	public function renderContent() {

	}
}
