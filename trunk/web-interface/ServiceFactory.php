<?php 

require_once('LocalService.php');
require_once('EC2Service.php');

class ServiceFactory {
	
	public static function createInstance($service_data) {
		$cloud = $service_data['cloud'];
		
		switch ($cloud) {
			case 'local':
				return new LocalService($service_data);
			case 'ec2':
				return new EC2Service($service_data);
			default:
				throw new Exception('Unknown cloud');
		}
	}
}