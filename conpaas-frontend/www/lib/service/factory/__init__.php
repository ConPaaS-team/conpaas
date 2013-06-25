<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('cloud');

class ServiceFactory {

	public static function createManager($service_data) {
		return new Manager($service_data);
	}

	public static function create($service_data) {
		$type = $service_data['type'];
		$manager = self::createManager($service_data);

		switch ($type) {
			case 'php':
				require_module('service/php');
				return new PHPService($service_data, $manager);
			case 'java':
				require_module('service/java');
				return new JavaService($service_data, $manager);
			case 'mysql':
				require_module('service/mysql');
				return new MysqlService($service_data, $manager);
			case 'taskfarm':
				require_module('service/taskfarm');
				return new TaskFarmService($service_data, $manager);
			case 'scalaris':
				require_module('service/scalaris');
				return new ScalarisService($service_data, $manager);
			case 'hadoop':
				require_module('service/hadoop');
				return new HadoopService($service_data, $manager);
			case 'xtreemfs':
				require_module('service/xtreemfs');
				return new XtreemFSService($service_data, $manager);
			case 'selenium':
				require_module('service/selenium');
				return new SeleniumService($service_data, $manager);
			case 'cds':
				require_module('service/cds');
				return new ContentDeliveryService($service_data, $manager);
/*
			case 'htcondor':
				require_module('service/htcondor');
				return new HTCondorService($service_data, $manager);
*/
/* BLUE_PRINT_INSERT		do not remove this line: it is a placeholder for installing new services */
			default:
				throw new Exception('Unknown service type');
		}
	}
}

?>
