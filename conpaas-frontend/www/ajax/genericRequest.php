<?php
/* Copyright (C) 2010-2015 by Contrail Consortium. */

require_once('../__init__.php');
require_module('service');
require_module('service/factory');

try {
    if (!isset($_SESSION['uid'])) {
        throw new Exception('User not logged in');
    }

    $sid = $_POST['sid'];
    $service_data = ServiceData::getServiceById($sid);
    $service = ServiceFactory::create($service_data);

    if ($service->getUID() !== $_SESSION['uid']) {
        throw new Exception('Not allowed');
    }

    $method = $_POST['method'];
    $allowed_methods = array("createVolume", "deleteVolume");
    if (!in_array($method, $allowed_methods)) {
        throw new Exception('Invalid method');
    }

    unset($_POST['sid']);
    unset($_POST['method']);
    $response = $service->$method($_POST);
    echo $response;
} catch (Exception $e) {
    echo json_encode(array('error' => $e->getMessage()));
}

?>
