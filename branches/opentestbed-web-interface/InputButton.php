<?php

function InputButton($text) {
	return new InputButton($text);
}

class InputButton {
	
	protected $id = '';
	protected $text;
	protected $visible = true;
	protected $disabled = false;
	
	public function __construct($text) {
		$this->text = $text;	
	}
	
	public function setVisible($visible) {
		$this->visible = $visible;
		return $this;
	}
	
	public function setId($id) {
		$this->id = $id;
		return $this;
	}
	
	public function setDisabled($disabled) {
		$this->disabled = $disabled;
		return $this;
	}
	
	private function invisibleClass() {
		if ($this->visible) {
			return '';
		}
		return 'invisible';
	}
	
	private function disabledMarker() {
		if ($this->disabled) {
			return ' disabled="disabled" ';
		}
		return '';
	}
	
	public function __toString() {
		return 
			'<input id="'.$this->id.'" type="button" '
			.' class="button '.$this->invisibleClass().'"'
			.' value="'.$this->text.'" '.$this->disabledMarker().'/>';
	}
}

