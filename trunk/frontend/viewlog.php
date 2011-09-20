<?php 

require_once('__init__.php');
require_once('Service.php');
require_once('ServiceFactory.php');

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::createInstance($service_data);

$log = $service->fetchLog();

?> 

<pre><?php echo $log; ?></pre>