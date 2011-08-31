<?php

require_once('../__init__.php');
require_once('../Service.php');
require_once('../ServiceData.php');

try {
	$sid = $_GET['sid'];
	$newname = $_POST['name'];
	ServiceData::updateName($sid, $newname);
	
	echo json_encode(array(
		'save' => 1,
		'name' => $newname,
	));
} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage(),
		'save' => 0,
	));
}