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

require_once('__init__.php');
require_module('db');
require_module('user');
require_module('service');
require_module('service/factory');

try {

	if ($_SERVER['REQUEST_METHOD'] != 'POST') {
		throw new Exception('Only calls with POST method accepted');
	}

	if (!array_key_exists('type', $_POST)) {
		throw new Exception('Missing parameters');
	}

	if (!isset($_SESSION['uid'])) {
		throw new Exception('User not logged in');
	}

	$type = $_POST['type'];

	$res = json_decode(HTTPS::post(Conf::DIRECTOR . '/start/' . $type, 
	    array(), false, $_SESSION['uid']));

    if (!$res) {
        throw new Exception('User not logged in');
    }

    /* error creating new service */
    if (property_exists($res, 'msg')) {
        throw new Exception($res->msg);
    }

	// HACK: keep a must_reset_password flag for the MySQL service
	// we should keep this information in the service's manager state
	if ($type == 'mysql') {
		$_SESSION['must_reset_passwd_for_'.$res->sid] = true;
	}

	echo json_encode(array(
		'sid' => $res->sid,
		'create' => 1,
	));
} catch (Exception $e) {
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'error' => $e->getMessage(),
	));
}
