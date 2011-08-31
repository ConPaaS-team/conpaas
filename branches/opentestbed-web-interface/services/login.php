<?php

require_once('../__init__.php');
require_once('../UserData.php');
require_once('../Page.php');
require_once('../DB.php');

function register() {
    if (!isset($_POST['username'])
        || !isset($_POST['email'])
        || !isset($_POST['fname'])
        || !isset($_POST['lname'])
        || !isset($_POST['affiliation'])
        || !isset($_POST['passwd'])) {
      return array(
      	'register' => 0,
      	'error' => 'Please complete the registration form'
      );
    }
    $username = $_POST['username'];
	$uinfo = UserData::getUserByName($username);
	if ($uinfo !== 	false) {
		return array(
			'register' => 0,
			'error' => 'username <b>'.$username.'</b> already exists'
		);
	}
	try {
	    UserData::createUser($username, $_POST['email'], $_POST['fname'], $_POST['lname'], $_POST['affiliation'], $_POST['passwd']);
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
	$mailr = mail('testbed@conpaas.eu', 'New user - ' . $username,
	  'New user:'
	  .'Username: ' . $_POST['username'] . "\r\n"
	  .'First name: ' . $_POST['fname'] . "\r\n"
	  .'Last name: ' . $_POST['lname'] . "\r\n"
	  .'email: ' . $_POST['email'] . "\r\n"
	  .'Affiliation: ' . $_POST['affiliation'] . "\r\n"
	  ."\r\n",
	  "From: frontend@conpaas.eu\r\n".
	  "Reply-To: frontend@conpaas.eu\r\n"
      );
	  if ( $mailr !== TRUE ) {
	    return array(
		'register' => 0,
	    'error' => 'Failed to send email'
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
	if ($uinfo === false or $uinfo['passwd'] !== md5($_POST['passwd'])) {
		return array(
			'auth' => 0, 
			'error' => "username and password don't match"
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
	$response = register();
}

echo json_encode($response);

?>