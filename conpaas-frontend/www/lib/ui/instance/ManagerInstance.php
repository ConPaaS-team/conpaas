<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



class ManagerInstance extends Instance {

	public function __construct($id, $ip, $cloud) {
		parent::__construct(array('id' => $id, 'ip' => $ip, 'cloud' => $cloud));
	}

	protected function renderCapabs() {
		return '<div class="tag black">Application manager</div>';
	}

    protected function renderAgentLogs() {
        return '';
    }

}

?>
