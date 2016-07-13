<?php


require_module('service');


function ColorTag ($state) {
    return new ColorTag($state);
}

class ColorTag {

	private $state;

	public function __construct($state) {
		$this->state = $state;
	}

	public function __toString() {
		$color_class = 'colortag-stopped';
		static $active_states = array(
			Service::STATE_RUNNING => true,
			Service::STATE_ADAPTING => true,
			Service::STATE_PROLOGUE => true,
			Service::STATE_EPILOGUE => true,
		);
		if (array_key_exists($this->state, $active_states)) {
			$color_class = 'colortag-active';
		}
		return
			'<td class="colortag '.$color_class.'"></td>';
    }
}
