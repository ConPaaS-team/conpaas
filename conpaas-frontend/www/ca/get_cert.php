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
require_module('logging');
require_module('ca');

/**
 * Determines if the client provided a valid SSL certificate
 *
 * @return boolean True if the client cert is there and is valid
 */
function has_valid_cert()
{
	if (!isset($_SERVER['SSL_CLIENT_M_SERIAL'])
		|| !isset($_SERVER['SSL_CLIENT_V_END'])
		|| !isset($_SERVER['SSL_CLIENT_VERIFY'])
		|| $_SERVER['SSL_CLIENT_VERIFY'] !== 'SUCCESS'
		|| !isset($_SERVER['SSL_CLIENT_I_DN'])) {
			return false;
		}
	//TODO: verify that requester is manager    
	if ($_SERVER['SSL_CLIENT_V_REMAIN'] <= 0) {
		return false;
	}
	return true;
}

if (!has_valid_cert()) {
	echo json_encode(array(
		'error' => 'Client did not provide a valid certificate'
	));
	exit();
}

dlog('Valid certificate provided by: '.$_SERVER['SSL_CLIENT_S_DN_CN']);

// Get the CSR - TODO: verify the CSR with the CN of requestor
if (!isset($_FILES['csr'])) {
	echo json_encode(array(
		'error' => 'CSR file not found'
	));
	exit();
}

$path = '/tmp/'.$_FILES['csr']['name'];
if (move_uploaded_file($_FILES['csr']['tmp_name'], $path) === false) {
	echo json_encode(array(
		'error' => 'could not move uploaded file'
	));
	exit();
}

$csr = file_get_contents($path);

//TODO: Implement crs verification
//if (!valid_req($csr)) {
//	echo json_encode(array(
//		'error' => 'CSR not valid'
//	));
//	exit();
//}

// Generate the request
echo create_x509_cert($csr);
unlink($path);
?>
