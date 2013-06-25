<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/instance');

class MysqlInstance extends Instance {

	public function __construct($info) {
		parent::__construct($info);
	}

	protected function renderCapabs() {
		$html = '';
		if ($this->info['isSlave']) {
			$html .= '<div class="tag orange">slave</div>';
		}
		if ($this->info['isMaster']) {
			$html .= '<div class="tag blue">master</div>';
		}
		return $html;
	}
}

?>
