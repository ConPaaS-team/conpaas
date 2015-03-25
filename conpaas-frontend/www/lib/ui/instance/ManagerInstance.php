<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



class ManagerInstance extends Instance {

	public function __construct($id, $ip) {
		parent::__construct(array('id' => $id, 'ip' => $ip));
	}

	protected function renderCapabs() {
		return '<div class="tag black">manager</div>';
	}
}

?>
