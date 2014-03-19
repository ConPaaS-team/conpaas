<?php
/* file = conpaas-frontend/www/contrail-logout.php */
/* Copyright (C) 2010-2013 by Contrail Consortium. */



# We start off with loading a file which registers the simpleSAMLphp classes with the autoloader.

# require_once('../../lib/_autoload.php');

require_once('/var/www/config.php');
require_once('/usr/share/simplesamlphp-1.11.0/lib/_autoload.php');

# We select our authentication source:

$as = new SimpleSAML_Auth_Simple('default-sp');

# We then require authentication:

# $as->requireAuth();

# And print the attributes:

# $attributes = $as->getAttributes();
# print_r($attributes);

# Setup the callback URL
$realReturn = '';
if (isset($_GET['returnTo'])) {
        $realReturn = '?returnTo=' . $_GET['returnTo'];
} elseif (isset($_POST['returnTo'])) {
        $realReturn = '?returnTo=' . $_POST['returnTo'];
}

$as->logout(array(
        'ReturnTo' => 'https://' . CONPAAS_HOST . '/contrail/contrail-loggedout.php' . $realReturn ,
        'ReturnStateParam' => 'LogoutState',
        'ReturnStateStage' => 'MyLogoutState',
        ));

?>
