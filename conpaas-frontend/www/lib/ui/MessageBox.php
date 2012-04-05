<?php

function MessageBox($text, $type=MessageBox::INFO) {
	return new MessageBox($text, $type);
}

class MessageBox {

	const INFO = 'info';
	const WARNING = 'warning';
	const ERROR = 'error';

	private $text;
	private $type;

	public function __construct($text, $type=self::INFO) {
		$this->text = $text;
		$this->type = $type;
	}

	public function __toString() {
		return
		'<div class="msgbox msgbox-'.$this->type.'">'
			.$this->text
		.'</div>';
	}

}