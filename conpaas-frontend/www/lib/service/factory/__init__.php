<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */

require_module('logging');
require_module('application');

class ServiceFactory {


	public static function create($full_service_data) {
		$service_data = $full_service_data['service'];
		$type = $service_data['type'];

		$application = new Application($full_service_data['application']);

		switch ($type) {
			case 'php':
				require_module('service/php');
				return new PHPService($service_data, $application);
			case 'java':
				require_module('service/java');
				return new JavaService($service_data, $application);
			case 'galera':
                require_module('service/galera');
                return new GaleraService($service_data, $application);
			case 'taskfarm':
				require_module('service/taskfarm');
				return new TaskFarmService($service_data, $application);
			case 'scalaris':
				require_module('service/scalaris');
				return new ScalarisService($service_data, $application);
			case 'hadoop':
				require_module('service/hadoop');
				return new HadoopService($service_data, $application);
			case 'xtreemfs':
				require_module('service/xtreemfs');
				return new XtreemFSService($service_data, $application);
			case 'selenium':
				require_module('service/selenium');
				return new SeleniumService($service_data, $application);
			case 'cds':
				require_module('service/cds');
				return new ContentDeliveryService($service_data, $application);
/*
			case 'htcondor':
				require_module('service/htcondor');
				return new HTCondorService($service_data, $manager);
*/
			case 'htc':
				require_module('service/htc');
				return new HTCService($service_data, $application);
			case 'generic':
				require_module('service/generic');
				return new GenericService($service_data, $application);
/* BLUE_PRINT_INSERT		do not remove this line: it is a placeholder for installing new services */
			default:
                throw new Exception('ServiceFactory: Unknown service type "' . $type . '"');
		}
	}
}

?>
