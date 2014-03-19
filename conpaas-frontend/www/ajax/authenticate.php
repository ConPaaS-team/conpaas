<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('user');
require_module('logging');

try {
    $user = new User();
    if ($user->isAuthenticated()) {
        echo json_encode(array('authenticated' => 1));
        exit();
    }

    if ( isset($_POST['username']) && isset($_POST['password']) ) {
        $authenticated = $user->authenticate($_POST['username'], $_POST['password']);
        if ($authenticated) {
            echo json_encode(array('authenticated' => 1));
            exit();
        }
    }
    if ( isset($_POST['uuid']) && ($_POST['uuid'] != "<none>") ) {
        $authenticated = $user->authenticate_uuid($_POST['uuid']);
        if ($authenticated) {
            echo json_encode(array('authenticated' => 1));
            exit();
        }
    }

    echo json_encode(array(
        'authenticated' => 0,
        'error' => 'username and password don\'t match')
    );
} catch (Exception $e) {
    dlog($e->getMessage());
        echo json_encode(array(
        'error' => $e->getMessage(),
    ));
}
