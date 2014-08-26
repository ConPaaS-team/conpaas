<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/instance');

class GaleraInstance extends Instance {

	public function __construct($info) {
		parent::__construct($info);
	}

	protected function renderCapabs() {
		$html = '';
		if ($this->info['isNode']) {
			$html .= '<div class="tag orange">node</div>';
		}
		if ($this->info['isGlb_node']) {
			$html .= '<div class="tag blue">Glb node</div>';
		}
		return $html;
	}
}

?>
