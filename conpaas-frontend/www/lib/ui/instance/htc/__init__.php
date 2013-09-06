<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



/*
 *	 TODO:	as this file was created from a BLUEPRINT file,
 *	 	you may want to change ports, paths and/or methods (e.g. for hub)
 *		to meet your specific service/server needs
 */
require_module('ui/instance');

class HTCInstance extends Instance {

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
