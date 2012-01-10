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

require_module('service');
require_module('ui/instance/php');

class PHPService extends Service {

	public function __construct($data, $cloud) {
		parent::__construct($data, $cloud);
	}

	public function hasDedicatedManager() {
		return true;
	}
	
	public function sendConfiguration($params) {
		return $this->managerRequest('post', 'update_php_configuration',
			$params);
	}
	
	public function createInstanceUI($node) {
		$info = $this->getNodeInfo($node);
		return new PHPInstance($info);
	}

	public function getInstanceRoles() {
		return array('proxy', 'web', 'backend');
	}
	
}

?> 