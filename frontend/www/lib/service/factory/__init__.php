<?php
/*
 * Copyright (C) 2010-2011 Contrail consortium.
 *
 * This file is part of ConPaaS, an integrated runtime environment
 * for elastic cloud applications.
 *
 * ConPaaS is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * ConPaaS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.
 */

require_module('cloud');

class ServiceFactory {

	public static function createManager($service_data) {
		switch ($service_data['cloud']) {
			case 'ec2':
				return new EC2Manager($service_data);
			case 'opennebula':
				return new OpenNebulaManager($service_data);
			default:
				throw new Exception('Unknown cloud provider');
		}
	}

	public static function create($service_data) {
		$cloud = $service_data['cloud'];
		$type = $service_data['type'];
		$manager = self::createManager($service_data);

		switch ($type) {
			case 'php':
				require_module('service/php');
				return new PHPService($service_data, $manager);
			case 'java':
				require_module('service/java');
				return new JavaService($service_data, $manager);
			case 'taskfarm':
				require_module('service/taskfarm');
				return new TaskFarmService($service_data);
			case 'scalarix':
				require_module('service/scalarix');
				return new ScalarixService($service_data);
			case 'hadoop':
				require_module('service/hadoop');
				return new HadoopService($service_data);
			default:
				throw new Exception('Unknown service type');
		}
	}
}

?>