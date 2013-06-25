<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/instance');

class PHPInstance extends Instance {

	public function __construct($info) {
		parent::__construct($info);
	}

	protected function renderCapabs() {
		$html = '';
		if ($this->info['isRunningProxy']) {
			$html .= '<div class="tag orange">proxy</div>';
		}
		if ($this->info['isRunningWeb']) {
			$html .= '<div class="tag blue">web</div>';
		}
		if ($this->info['isRunningBackend']) {
			$html .= '<div class="tag purple">php</div>';
		}
		return $html;
	}
}

?>
