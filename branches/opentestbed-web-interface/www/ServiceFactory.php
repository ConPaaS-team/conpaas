<?php 

require_once('LocalService.php');
require_once('EC2Service.php');
require_once('OpenNebulaService.php');
require_once('Service.php');

class ServiceFactory {
	
	public static function createInstance($service_data) {
		$cloud = $service_data['cloud'];
		$type = $service_data['type'];
		$cloud_instance = null;
		
		switch ($cloud) {
			case 'local':
				$cloud_instance = new LocalCloud($service_data);
				break;
			case 'ec2':
				$cloud_instance = new EC2($service_data);
				break;
			case 'opennebula':
			    $cloud_instance = new OpenNebula($service_data);
				break;
			default:
				throw new Exception('Unknown cloud');
		}
		switch ($type) {
		  case 'php':
		    return new PHPService($service_data, $cloud_instance);
		  case 'java':
		   return new JavaService($service_data, $cloud_instance);
		  default:
				throw new Exception('Unknown service type');
		}
	}
}