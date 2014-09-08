<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('user');
require_module('logging');

try {
    $user = new User();
    if ($user->isAuthenticated()) {
        user_error('-- user passed');
        echo json_encode(array('authenticated' => 1));
        exit();
    }

    user_error('check username and password');
    if ( isset($_POST['username']) && isset($_POST['password']) ) {
        $authenticated = $user->authenticate($_POST['username'], $_POST['password']);
        if ($authenticated) {
            user_error('- uname + pw passed');
            echo json_encode(array('authenticated' => 1));
            exit();
        }
        user_error('- uname + pw failed');
    }
    user_error('check uuid');
    if ( isset($_POST['uuid']) && ($_POST['uuid'] != "<none>") ) {
        $authenticated = $user->authenticate_uuid($_POST['uuid']);
        if ($authenticated) {
            user_error('- uuid passed');
            echo json_encode(array('authenticated' => 1));
            exit();
        }
        user_error('- uuid failed');
    }
    user_error('check openid');
    if ( isset($_POST['openid']) && ($_POST['openid'] != "<none>") ) {
        $authenticated = $user->authenticate_openid($_POST['openid']);
        if ($authenticated) {
            user_error('- openid passed');
            echo json_encode(array('authenticated' => 1));
            exit();
        }
        user_error('- openid failed');
    }
    # TODO add openid 

    echo json_encode(array(
        'authenticated' => 0,
        'error' => 'username and password don\'t match')
    );
} catch (Exception $e) {
    user_error('-- authentication exception');
    dlog($e->getMessage());
        echo json_encode(array(
        'error' => $e->getMessage(),
    ));
}
