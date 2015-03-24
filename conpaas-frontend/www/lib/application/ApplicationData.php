<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('https');

class ApplicationData {
	public static function getApplications($uid, $aid) {
		$res = HTTPS::post(Conf::DIRECTOR . '/listapp', array(), false, $uid);

		$applications = array();
		foreach(json_decode($res) as $app) {
			if ($aid == NULL || $app->aid == $aid){
				$app = (array)$app;
				array_push($applications, $app);
			}
		}
		return $applications;
	}
}

?>
