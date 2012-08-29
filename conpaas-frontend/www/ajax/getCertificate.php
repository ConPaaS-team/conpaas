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
require_module('ca');
require_module('logging');
require_module('service');

function get_user_info($uid) {
	$query = sprintf("SELECT * FROM users WHERE uid='%s' LIMIT 1",
		mysql_escape_string($uid));
	$res = mysql_query($query, DB::getConn());
	if ($res === false) {
		throw new DBException(DB::getConn());
	}
	$entries = DB::fetchAssocAll($res);
	if (count($entries) != 1) {
		throw new Exception('User does not exist');
	}
	return $entries[0];
}

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$uid = $_SESSION['uid'];

$user_info = get_user_info($uid);

// Generate the request
$cert =  generate_certificate($uid, '0', 'user',
			$user_info['email'],
			$user_info['fname'].' '.$user_info['lname'],
			$user_info['affiliation']);

$path = tempnam(sys_get_temp_dir(), 'conpaas_cert.zip.');

$zip = new ZipArchive;
$res = $zip->open($path, ZipArchive::CREATE);
if ($res === TRUE) {
	$zip->addFromString('cert.pem', $cert['cert']);
	$zip->addFromString('key.pem', $cert['key']);
	$zip->addFromString('ca_cert.pem', $cert['ca_cert']);
	$zip->close();
} else {
	throw new Exception('Could not create archive');
}

header("Content-type: application/zip");
header('Content-Disposition:attachment;filename="' . 'certs.zip' . '"');
print file_get_contents($path);

unlink($path);

?>
