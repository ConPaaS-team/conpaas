<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/instance');

class HadoopInstance extends Instance {

	public function __construct($info) {
		parent::__construct($info);
	}

	protected function renderCapabs() {
		$html = '';
		if (isset($this->info['workers'])) {
			$html .= '<div class="tag orange">worker</div>';
		}
		if (isset($this->info['masters'])) {
			$html .= '<div class="tag blue">master</div>';
		}
		return $html;
	}
}

?>
