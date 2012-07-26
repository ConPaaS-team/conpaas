<?php

class ZibCloud extends OpennebulaCloud {

	public function __construct() {
	}

	public function getName() {
		return 'ZIB OpenNebula cluster';
	}

	public function getAvailableRegions() {
		return array(
			new Region('DE', 'Germany', 'Europe', 'zib')
		);
	}
}