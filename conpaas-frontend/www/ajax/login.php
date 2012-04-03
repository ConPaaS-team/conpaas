<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
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
