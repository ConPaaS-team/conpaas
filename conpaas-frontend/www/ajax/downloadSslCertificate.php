<?php
/* Copyright (C) 2010-2014 by Contrail Consortium. */



require_once('../__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('https');

try {
    if (!isset($_SESSION['uid'])) {
        throw new Exception('User not logged in');
    }

    $cert_type = $_GET['cert_type'];
    $user = $_GET['user'];
    $group = $_GET['group'];
    $passphrase = $_GET['passphrase'];
    $adminflag = $_GET['adminflag'];
    $filename = $_GET['filename'];
    $sid = $_GET['sid'];
    $service_data = ServiceData::getServiceById($sid);
    $service = ServiceFactory::create($service_data);

    if ($service->getUID() !== $_SESSION['uid']) {
        throw new Exception('Not allowed');
    }

    if (is_null($passphrase)) {
        $passphrase = '';
    }

    if (empty($adminflag)) {
        $adminflag = 'no';
    }

    if (empty($filename)) {
        $filename = $cert_type . '_cert.p12';
    }

    if ($cert_type == 'user') {
        if (empty($user)) {
            throw new Exception('The user field must not be empty!');
        }

        if (is_null($group)) {
            $group = '';
        }

        $method = 'get_user_cert';
        $params = array('user' => $user,
                        'group' => $group,
                        'passphrase' => $passphrase,
                        'adminflag' => $adminflag);
    } else {
        $method = 'get_client_cert';
        $params = array('passphrase' => $passphrase,
                        'adminflag' => $adminflag);
    }

    $response = HTTPS::jsonrpc($service->getManager(), 'post',
        $method, $params);

    $json_response = json_decode($response);

    if (!is_null($json_response->{'error'})) {
        throw new Exception($json_response->{'error'});
    }

    $base64_cert = $json_response->{'result'}->{'cert'};

    header("Content-Disposition:attachment;filename=$filename");
    header("Content-Type: application/x-pkcs12");
    echo base64_decode($base64_cert);
} catch (Exception $e) {
    echo $e->getMessage();
}
?>
