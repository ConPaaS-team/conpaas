<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/instance');

class GenericInstance extends Instance {

	public function __construct($info) {
		parent::__construct($info);
	}

	protected function renderCapabs() {
		$html = 'hello';
		
		return $html;
	}
}

?>
