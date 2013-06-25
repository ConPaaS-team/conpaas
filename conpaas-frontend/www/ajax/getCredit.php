<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('user');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$uinfo = UserData::getUserByName($_SESSION['username']);

echo json_encode(array(
                    'credit' => $uinfo['credit']));

?>
