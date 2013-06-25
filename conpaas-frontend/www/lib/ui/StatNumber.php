<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



function StatNumber($value, $note='', $metric='') {
	return new StatNumber($value, $note, $metric);
}

class StatNumber {

	private $id = '';
	private $value = 0;
	private $note = '';
	private $metric = '';

	public function __construct($value, $note, $metric) {
		$this->value = $value;
		$this->note = $note;
		$this->metric = $metric;
	}

	public function setId($id) {
		$this->id = $id;
		return $this;
	}

	public function __toString() {
		return
		'<div class="statistic statnumber">'
			.'<div class="note">'.$this->note.'</div>'
			.'<div class="value" id="'.$this->id.'">'.$this->value.'</div>'
			.'<div class="metric">'.$this->metric.'</div>'
		.'</div>';
	}
}
