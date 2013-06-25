<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/instance');

class SeleniumInstance extends Instance {

	public function __construct($info) {
		parent::__construct($info);
	}

	protected function renderCapabs() {
		$html = '';
        if ($this->info['is_hub']) {
            $html .= '<div class="tag blue">hub</div>';
        }
        else {
            $html .= '<div class="tag orange">node</div>';
        }
		return $html;
	}
}

?>
