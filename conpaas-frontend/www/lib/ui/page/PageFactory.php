<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



class PageFactory {

	public static function create($service) {
		$type = $service->getType();

		switch ($type) {
			case 'php':
				require_module('ui/page/hosting');
				return new PhpPage($service);
			case 'java':
				require_module('ui/page/hosting');
				return new JavaPage($service);
			case 'mysql':
				require_module('ui/page/mysql');
				return new MysqlPage($service);
			case 'taskfarm':
				require_module('ui/page/taskfarm');
				return new TaskFarmPage($service);
			case 'scalaris':
				require_module('ui/page/scalaris');
				return new ScalarisPage($service);
			case 'hadoop':
				require_module('ui/page/hadoop');
				return new HadoopPage($service);
			case 'xtreemfs':
				require_module('ui/page/xtreemfs');
				return new XtreemFSPage($service);
			case 'selenium':
				require_module('ui/page/selenium');
				return new SeleniumPage($service);
			case 'cds':
				require_module('ui/page/cds');
				return new CDSPage($service);
/*
			case 'htcondor':
				require_module('ui/page/htcondor');
				return new HTCondorPage($service);
*/
			case 'htc':
				require_module('ui/page/htc');
				return new HTCPage($service);
/* BLUE_PRINT_INSERT		do not remove this line: it is a placeholder for installing new services */
			default:
				throw new Exception('Unknown service type');
		}
	}
}
