<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('user');
require_module('recaptcha');
require_module('logging');

try {
	$user = new User();
	if ($user->isAuthenticated()) {
		throw new Exception('you already have an user');
	}
	// check for missing fields first
	$fields = array('username', 'password', 'email', 'fname', 'lname', 'affiliation');

    if (defined('CAPTCHA_PUBLIC_KEY') && defined('CAPTCHA_PRIVATE_KEY')) {
        // only require recaptcha fields if checks are enabled
        $fields = array_merge($fields, array('recaptcha_response', 'recaptcha_challenge'));
    }

	foreach ($fields as $field) {
		if (!isset($_POST[$field])) {
			throw new Exception('missing field: '.$field);
		}
	}
	// check recaptcha (if necessary)
    if (defined('CAPTCHA_PUBLIC_KEY') && defined('CAPTCHA_PRIVATE_KEY')) {
        $resp = recaptcha_check_answer(CAPTCHA_PRIVATE_KEY, $_SERVER['REMOTE_ADDR'],
            $_POST['recaptcha_challenge'], $_POST['recaptcha_response']);
        if (!$resp->is_valid) {
            dlog('CAPTCHA error: '.$resp->error);
            echo json_encode(array(
                'registered' => 0,
                'message' => 'reCAPTCHA was wrong',
                'recaptcha' => 1
            ));
            exit();
        }
    }
	// check if the user already exists
	$uinfo = UserData::getUserByName($_POST['username']);
	if ($uinfo !== 	false) {
		echo json_encode(array(
			'registered' => 0,
			'error' => 'username <b>'.$_POST['username'].'</b> already exists'
		));
		exit();
	}
	// create the user
	$conf = Logging::loadConf();
	UserData::createUser($_POST['username'], $_POST['email'], $_POST['fname'],
		$_POST['lname'], $_POST['affiliation'], $_POST['password'],
	    $conf['initial_credit']);
	$_SESSION['username'] = $_POST['username'];
	$_SESSION['password'] = $_POST['password'];
	$user->loadByName($_POST['username']);
	$user->establishSession();
	$mailsent = $user->sendWelcomeEmail();
	if (!$mailsent) {
	  		// throw an error in the log, but still login the user
	  		$msg = 'Failed to send registration email to '.$_POST['email'];
	  		dlog($msg);
	  		error_log($msg);
	}
	// registered ok
	echo json_encode(array('registered' => 1));
} catch (Exception $e) {
	dlog($e->getMessage());
	echo json_encode(array(
		'registered' => 0,
		'error' => $e->getMessage()
	));
}
