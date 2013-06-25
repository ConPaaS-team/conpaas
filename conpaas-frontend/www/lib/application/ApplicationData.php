<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('https');

class ApplicationData {
	public static function getApplications($uid) {
		$res = HTTPS::post(Conf::DIRECTOR . '/listapp', array(), false, $uid);

		$applications = array();
		foreach(json_decode($res) as $app) {
			$app = (array)$app;
			array_push($applications, $app);
		}
		return $applications;
	}
}

?>
