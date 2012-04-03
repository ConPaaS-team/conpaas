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

ignore_user_abort(true);

require_once('../__init__.php');
require_module('service');
require_module('service/factory');
require_module('user');

/* accept POST requests only */
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    die();
}

$response = 'empty';

if(!isset($_POST['sid']) || !isset($_POST['decrement'])) {
    $response = array('error' => 'Missing arguments');
}
else if ($_POST['decrement'] < 1) {
    $response = array('error' => 'Invalid arguments');
}
else {
    try {
        /* accept requests from manager nodes only */
        $service_data = ServiceData::getServiceById($_POST['sid']);
        $service = ServiceFactory::create($service_data);
        $manager_host = parse_url($service->getManager(), PHP_URL_HOST);
        /* test source of request is from a manager node */
        if (gethostbyname($manager_host) !== $_SERVER['REMOTE_ADDR']) {
            $response = array('error' => 'Not allowed');
        }
        else {
            $ret = UserData::updateUserCredit($service->getUID(), -$_POST['decrement']);
            if ($ret === false) {
                $response = array('error' => 'Not enough credit');
            }
            else {
                $response = array('error' => null);
            }
        }
    } catch (Exception $e) {
        $response = array(
    		'error' => 'Internal error'
        );
    }
}

echo json_encode($response);
?>
