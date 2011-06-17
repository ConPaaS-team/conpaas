<?php 

require_once('../__init__.php');
require_once('../logging.php');
require_once('../Service.php');
require_once('../ServiceData.php');
require_once('../ServiceFactory.php');

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::createInstance($service_data);

$path = '/tmp/'.$_FILES['code']['name'];
if (move_uploaded_file($_FILES['code']['tmp_name'], $path) === false) {
	echo json_encode(array(
		'error' => 'could not move uploaded file'
	));
}
$params = array_merge($_POST,
	array('code' => '@'.$path)
);
$response = $service->uploadCodeVersion($params);
unlink($path);
echo $response;

?>