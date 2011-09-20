<?php 
  // Copyright (C) 2010-2011 Contrail consortium.
  //
  // This file is part of ConPaaS, an integrated runtime environment 
  // for elastic cloud applications.
  //
  // ConPaaS is free software: you can redistribute it and/or modify
  // it under the terms of the GNU General Public License as published by
  // the Free Software Foundation, either version 3 of the License, or
  // (at your option) any later version.
  //
  // ConPaaS is distributed in the hope that it will be useful,
  // but WITHOUT ANY WARRANTY; without even the implied warranty of
  // MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  // GNU General Public License for more details.
  //
  // You should have received a copy of the GNU General Public License
  // along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.

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