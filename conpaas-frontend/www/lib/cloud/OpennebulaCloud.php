<?php

abstract class OpennebulaCloud extends Cloud {

	public function __construct() {
	}

	public function getName() {
		return 'Opennebula';
	}

	public function getLogo() {
		return '<img class="cloud" src="images/opennebula.png" />';
	}
}