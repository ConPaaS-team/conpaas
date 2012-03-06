<?php
/*
 * Copyright (C) 2010-2011 Contrail consortium.
 *
 * This file is part of ConPaaS, an integrated runtime environment
 * for elastic cloud applications.
 *
 * ConPaaS is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * ConPaaS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once('../__init__.php');
require_module('db');
require_module('user');
require_module('logging');

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
	$conf = Logging::loadConf();
	try {
	    UserData::createUser($username, $_POST['email'], $_POST['fname'],
	    	$_POST['lname'], $_POST['affiliation'], $_POST['passwd'],
	    	$conf['initial_credit']);
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
	$mailr = mail($conf['admin_email'], 'New user at ZIB - ' . $username,
	  'New user:'
	  .'Username: ' . $_POST['username'] . "\r\n"
	  .'First name: ' . $_POST['fname'] . "\r\n"
	  .'Last name: ' . $_POST['lname'] . "\r\n"
	  .'email: ' . $_POST['email'] . "\r\n"
	  .'Affiliation: ' . $_POST['affiliation'] . "\r\n"
	  ."\r\n",
	  "From: ".$conf['admin_email']."\r\n".
	  "Reply-To: ".$conf['admin_email']."\r\n"
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
