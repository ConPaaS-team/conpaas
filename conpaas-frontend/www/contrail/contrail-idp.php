<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */

require_once('../__init__.php');
require_module('logging');



    # We start off with loading a file which registers the simpleSAMLphp classes with the autoloader.

    require_once('/usr/share/simplesamlphp-1.11.0/lib/_autoload.php');

try {

    $return_url = "";
    if (isset($_GET['ReturnTo'])) {
        $return_url = $_GET['ReturnTo'];
    } elseif (isset($_POST['ReturnTo'])) {
        $return_url = $_POST['ReturnTo'];
    }
    # We select our authentication source:

    $as = new SimpleSAML_Auth_Simple('default-sp');

    # We then require authentication:

    if (isset($return_url)) {
        $auth = $as->requireAuth(array( 'ReturnTo' => $return_url));
    } else {
        $auth = $as->requireAuth();
    }

    # And get the attributes:

    $attributes = $as->getAttributes();

    echo json_encode($attributes);
    exit();

} catch (Exception $e) {
    dlog($e->getMessage());
        echo json_encode(array(
        'error' => $e->getMessage(),
    ));
}

?>
