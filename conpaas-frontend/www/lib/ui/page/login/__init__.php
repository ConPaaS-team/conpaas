<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/page');

class LoginPage extends Page {

	public function __construct() {
		parent::__construct();
		$this->addJS('js/login.js');
	}
}
