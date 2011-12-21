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

function StatusLed(Service $service) {
	return new StatusLed($service);
}

class StatusLed {
	
	private $service;
	
	public function __construct(Service $service) {
		$this->service = $service;
	}
	
	private function getImage() {
		$state = $this->service->getState();
		if (!$this->service->isReachable()) {
			if ($state == Service::STATE_INIT ||
			    $state == Service::STATE_PREINIT) {
			    	return 'images/ledlightblue.png';
			    }
			return 'images/ledorange.png';
		}
		/* for reachable case */
		switch ($state) {
			case Service::STATE_INIT:
				return 'images/ledlightblue.png';
			case Service::STATE_RUNNING:
				return 'images/ledgreen.png';
			case Service::STATE_STOPPED:
				return 'images/ledgray.png';
			case Service::STATE_ERROR:
				return 'images/ledred.png';
		}
	}
	
	public function __toString() {
		return '<img class="led" title="'.$this->service->getStatusText().'" '
			.' src="'.$this->getImage().'" style="vertical-align: middle;" />';
	}
}
