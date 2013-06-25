<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('logging');
require_module('https');

class Application {

	protected $aid,
		  $name;

	private $errorMessage = null;

	public static function stateIsStable($remoteState) {
		return true;
	}

	public function __construct($data) {
		foreach ($data as $key => $value) {
			$this->$key = $value;
		}
	}

	public function getErrorMessage() {
		return $this->errorMessage;
	}

	public function needsPolling() {
		return false;
	}

	public function getAID() {
		return $this->aid;
	}

	public function getName() {
		return $this->name;
	}

	public function toArray() {
		return array(
			'aid' => $this->aid,
			'name' => $this->name,
		);
	}
}
