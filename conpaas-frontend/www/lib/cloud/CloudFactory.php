<?php

class CloudFactory {

	public static function getAvailableClouds() {
		return array(
			new EC2Cloud(),
			new ZibCloud()
		);
	}
}