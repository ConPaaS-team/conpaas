<?php

require_once('../__init__.php');
require_once('../UserData.php');
require_once('../Page.php');
require_once('../DB.php');

function register($username) {
	$uinfo = UserData::getUserByName($username);
	if ($uinfo !== 	false) {
		return array(
			'register' => 0,
			'error' => 'username <b>'.$username.'</b> already exists'
		);
	}
	try {
	    UserData::createUser($username);
	} catch (DBException $e) {
	    return array(
			'register' => 0,
			'error' => 'user could not be added into the database',
		);
	}
	$uinfo = UserData::getUserByName($username);
	if ($uinfo === false) {
		return array(
			'register' => 0,
			'error' => 'user could not be added into the database',
		);
	}
	/* already login the user */
	$_SESSION['uid'] = $uinfo['uid'];
	return array(
		'register' => 1,
	);
}

function auth($uid, $username) {
	if ($uid !== null) {
		return array('auth' => 1);
	}
	$uinfo = UserData::getUserByName($username);
	if ($uinfo === false) {
		return array(
			'auth' => 0, 
			'error' => 'username <b>'.$username.'</b> doesn\'t exist'
		);
	}
	$_SESSION['uid'] = $uinfo['uid'];
	return array('auth' => 1);
}

$action = $_POST['action'];
$uid = null;
if (isset($_SESSION['uid'])) {
	$uid = $_SESSION['uid'];
}

if ($action == 'auth') {
    $username = $_POST['username'];
	$response = auth($uid, $username);
} else if ($action == 'logout') {
	unset($_SESSION['uid']);
	$response = array('logout' => 1);
} else if ($action == 'register') {
    $username = $_POST['username'];
	$response = register($username);
}

echo json_encode($response);

?>