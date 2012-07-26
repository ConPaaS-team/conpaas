<?php

abstract class Cloud {

	public $regions = array();

	abstract public function getName();
	abstract public function getLogo();
	abstract public function getAvailableRegions();
}