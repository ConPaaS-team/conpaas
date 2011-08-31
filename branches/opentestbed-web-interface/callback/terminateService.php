<?php 

ignore_user_abort(true);

require_once('../__init__.php');
require_once('../UserData.php');
require_once('../ServiceData.php');
require_once('../ServiceFactory.php');

/* accept POST requests only */
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    die();
} 

if(!isset($_POST['sid'])) {
    $response = array('error' => 'Missing arguments');
}
else {
    try {
        /* accept requests from manager node only */
        $service_data = ServiceData::getServiceById($_POST['sid']);
        $service = ServiceFactory::createInstance($service_data);
        $manager_host = parse_url($service->getManager(), PHP_URL_HOST);
        /* test source of request is from a manager node */
        if (gethostbyname($manager_host) !== $_SERVER['REMOTE_ADDR']) {
          $response = array('error' => 'Not allowed');
        }
        else {
            $service->terminateService();
            $response = array('error' => null);
        }
    } catch (Exception $e) {
        $response = array(
    		'error' => 'Internal error'
        );
    }
}

echo json_encode($response);

?>