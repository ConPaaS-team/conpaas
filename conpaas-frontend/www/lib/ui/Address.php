<?php

function Address($address) {
	return new Address($address);
}

class Address {

	private $address;
	private $title = '';
	private $width = 350; // px

	public function __construct($address) {
		$this->address = $address;
	}

	public function setWidth($width) {
		$this->width = $width;
		return $this;
	}

	public function setTitle($title) {
		$this->title = $title;
		return $this;
	}

	public function __toString() {
		return
		'<div class="addressbox" title="'.$this->title.'">'
			.'<i class="at">@</i>'
			.'<input type="text" readonly="readonly" class="address" '
				.'onclick="this.select()" value="'.$this->address.'" '
				.'style="width: '.$this->width.'px;" />'
		.'</div>';
	}
}