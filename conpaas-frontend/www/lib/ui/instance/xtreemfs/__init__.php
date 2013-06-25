<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/instance');

class XtreemFSInstance extends Instance {

	public function __construct($info) {
		parent::__construct($info);
	}


	protected function renderCapabs() {
		$html = '';
		if ($this->info['dir']) {
			$html .= '<div class="tag purple">DIR</div>';
		}
		if ($this->info['mrc']) {
			$html .= '<div class="tag blue">MRC</div>';
		}
		if ($this->info['osd']) {
			$html .= '<div class="tag orange">OSD</div>';
		}
		return $html;
	}
}

?>
