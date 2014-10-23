<?php

require_once('../__init__.php');
if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}


	

try {
	$fileContent = file_get_contents($_FILES['profile']['tmp_name']);
	//upload it to the application manager
	
	echo $fileContent;

} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage()
	));
}




?>
