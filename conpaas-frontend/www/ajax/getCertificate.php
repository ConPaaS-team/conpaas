<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('https');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$res = HTTPS::post(Conf::DIRECTOR . '/getcerts', 
    array('username' => $_SESSION['username'], 'password' => $_SESSION['password']));

header("Content-type: application/zip");
header('Content-Disposition:attachment;filename="' . 'certs.zip' . '"');
print ($res);
?>
