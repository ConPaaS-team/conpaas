<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



function LinkUI($text, $href) {
	return new LinkUI($text, $href);
}

class LinkUI {

	const POS_RIGHT = 'right';
	const POS_LEFT = 'left';

	private $text;
	private $href;
	private $external = false;
	private $class = 'link';
	private $iconURL = 'images/link_s.png';
	private $iconPosition = self::POS_RIGHT;

	public function __construct($text, $href) {
		$this->text = $text;
		$this->href = $href;
	}

	public function setIconPosition($position) {
		if ($position !== self::POS_LEFT && $position !== self::POS_RIGHT) {
			return $this;
		}
		$this->iconPosition = $position;
		return $this;
	}

	public function setExternal($external) {
		$this->external = $external;
		return $this;
	}

	public function setIconURL($url) {
		$this->iconURL = $url;
		return $this;
	}

	public function addClass($class) {
		$this->class .= ' '.$class;
		return $this;
	}

	private function renderSymbol() {
		return
			'<img src="'.$this->iconURL.'" style="vertical-align: middle;" />';
	}

	public function __toString() {
		$target = $this->external ? 'target="new"' : '';
		$leftSymbol = '';
		$rightSymbol = '';
		if ($this->iconPosition == self::POS_LEFT) {
			$leftSymbol = $this->renderSymbol();
		} else {
			$rightSymbol = $this->renderSymbol();
		}
		return
		'<div class="'.$this->class.'">'
			.$leftSymbol
			.'<a href="'.$this->href.'" '.$target.'>'.$this->text.'</a>'
			.$rightSymbol
		.'</div>';
	}
}
