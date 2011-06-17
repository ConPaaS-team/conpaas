<?php 

function LinkUI($text, $href) {
	return new LinkUI($text, $href);
}

class LinkUI {
	
	private $text;
	private $href;
	private $external = false;
	private $class = 'link';
	
	public function __construct($text, $href) {
		$this->text = $text;
		$this->href = $href;
	}
	
	public function setExternal($external) {
		$this->external = $external;
		return $this;
	}
	
	public function addClass($class) {
		$this->class .= ' '.$class;
		return $this;
	}
	
	private function renderSymbol() {
		return 
			'<img src="images/link_s.png" style="vertical-align: middle;" />';
	}
	
	public function __toString() {
		$target = $this->external ? 'target="new"' : '';
		return
		'<div class="'.$this->class.'">'
			.'<a href="'.$this->href.'" '.$target.'>'.$this->text.'</a>'
			.$this->renderSymbol()
		.'</div>';
	}
}