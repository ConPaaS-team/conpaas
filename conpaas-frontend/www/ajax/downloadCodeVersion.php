<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('../__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('https');

if (!isset($_SESSION['uid'])) {
    throw new Exception('User not logged in');
}

$codeVersionId = $_GET['codeVersionId'];
$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

/* Get a list of the available code versions */
try {
    $result = json_decode(HTTPS::jsonrpc($service->getManager(), 'get',
        'list_code_versions', array()));
} catch (Exception $e) {
    echo json_encode(array('error' => $e->getMessage()));
    exit();
}

$code_versions = $result->result->codeVersions;

/* Determine the file name of the requested code version */
$filename = null;
foreach ($code_versions as $code_version) {
    if ($code_version->codeVersionId === $codeVersionId) {
        $filename = $code_version->filename;
        break;
    }
}

if (is_null($filename)) {
    throw new Exception('Cannot determine filename for code version ' . $codeVersionId);
}

/* Guess the content-type */
if (preg_match('/\.(zip|war)$/', $filename)) {
    $content_type = 'application/zip';
}
else if (preg_match('/\.tar$/', $filename)) {
    $content_type = 'application/x-tar';
}
else {
    throw new Exception("Cannot determine content-type for '$filename', code version '$codeVersionId'");
}

/* Finally call the 'download_code_version' method and return the result */
try {
    $params = array('codeVersionId' => $codeVersionId);
    $response = HTTPS::jsonrpc($service->getManager(), 'get',
        'download_code_version', $params);

    header("Content-Disposition:attachment;filename=$filename");
    header("Content-Type: $content_type");
    echo $response;
} catch (Exception $e) {
    echo json_encode(array('error' => $e->getMessage()));
}
?>
