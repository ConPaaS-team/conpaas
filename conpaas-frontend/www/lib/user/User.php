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
	}

	public function authenticate($username, $password) {
		$uinfo = UserData::getUserByName($username);
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