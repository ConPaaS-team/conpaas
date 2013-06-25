<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/instance');

class ScalarisInstance extends Instance {

	public function __construct($info) {
		parent::__construct($info);
	}

	protected function renderCapabs() {
		return '<div class="tag blue">DB node</div>';
	}
}

?>
