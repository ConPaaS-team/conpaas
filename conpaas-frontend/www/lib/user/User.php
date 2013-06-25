<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('logging');

class User {

	private $uid;
	private $name;
	private $firstName;
	private $lastName;
	private $affiliation;
	private $email;

	public function __construct() {
		$this->uid = isset($_SESSION['uid']) ? $_SESSION['uid'] : false;
	}

	public function loadByName($username) {
		$uinfo = UserData::getUserByName($username);
		if ($uinfo === false) {
			throw new Exception('No user '.$username.' found');
		}
		$this->uid = $uinfo['uid'];
		$this->name = $username;
		$this->firstName = $uinfo['fname'];
		$this->lastName = $uinfo['lname'];
		$this->email = $uinfo['email'];
		$this->affiliation = $uinfo['affiliation'];
	}

	public function getUID() {
		return $this->uid;
	}

	public function isAuthenticated() {
		return $this->uid !== false;
	}

	public function establishSession() {
		$_SESSION['uid'] = $this->uid;
	}

	public function closeSession() {
		unset($_SESSION['uid']);
		unset($_SESSION['username']);
		unset($_SESSION['password']);
	}

	public function authenticate($username, $password) {
        $_SESSION['username'] = $username;
        $_SESSION['password'] = $password;

		$uinfo = UserData::getUserByName($username, true);
		if ($uinfo === false) {
			return false;
		}
		if ($uinfo['passwd'] != md5($password)) {
			return false;
		}
		$this->uid = $uinfo['uid'];
		$this->establishSession();
		return true;
	}

	public function sendWelcomeEmail() {
		$conf = Logging::loadConf();
		$to = $this->email;
		$from = $conf['admin_email'];
		$subject = $conf['welcome_email_subject'];
		$message = 'Dear '.$this->firstName.",\n\n"
		.file_get_contents(Conf::CONF_DIR.'/'.$conf['welcome_email_message'])
			."\n\n\n"
			.'Username: '.$this->name."\n"
			.'First name: '.$this->firstName."\n"
			.'Last name: '.$this->lastName."\n"
			.'Email: '.$this->email."\n"
			.'Affiliation: '.$this->affiliation."\n"
			.'IP address: '.$_SERVER['REMOTE_ADDR'];
		$headers = 'From: '.$from."\r\n"
	  		.'Reply-To: '.$from."\r\n"
	  		.'CC: '.$from."\r\n";
		return mail($to, $subject, $message, $headers);
	}
}
