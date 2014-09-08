<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('user');

try {
	$user = new User();
        $username = $_SESSION['username'];
        if (isset($_SESSION['openid'])) {
            $openid = $_SESSION['openid'];
        } else {
            $openid = null;
        }
        if (isset($_SESSION['uuid'])) {
            $uuid = $_SESSION['uuid'];
        } else {
            $uuid = null;
        }
	$user->closeSession();
	echo json_encode(array('logout' => 1, 'openid' => $openid, 'uuid' => $uuid, 'username' => $username)); 
} catch (Exception $e) {
	dlog($e->getMessage());
	error_log($e->getTraceAsString());
	echo json_encode(array(
		'logout' => 0,
		'error' => $e->getMessage()
	));
}
