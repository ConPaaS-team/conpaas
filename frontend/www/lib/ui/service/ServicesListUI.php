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

class ServicesListUI {
	
	private $services;
	
	public function __construct(array $services) {
		$this->services = $services;
	}
	
	public function addService(Service $service) {
		$this->services[] = $service;
		return $this;
	}
	
	public function isEmpty() {
		return count($this->services) == 0;
	}
	
	private function renderItems() {
		$html = '';
		for ($i = 0; $i < count($this->services); $i++) {
			$serviceUI = new DashboardServiceUI($this->services[$i]);
			if ($i == count($this->services) - 1) {
				$serviceUI->setLast();
			}
			$html .= $serviceUI->__toString();
		}
		return $html;
	}
	
	public function needsRefresh() {
		foreach ($this->services as $service) {
			if ($service->needsPolling()) {
				return true;
			}
		}
		return false;
	}
	
	private function generateRefreshScript() {
		if (!$this->needsRefresh()) {
			return '';
		}
		return 
			'<script type="text/javascript">'.
				'$(document).ready(function() {'.
					'setTimeout("refreshServices();", 3000);'.
				'});'.
			'</script>';
	}
	
	public function render() {
		return
  		'<div class="services">'.
  			'<div class="brief">all services</div>'.
  			'<table class="slist" cellpadding="0" cellspacing="1">'.
				$this->renderItems().
  			'</table>'.
  		'</div>'.
		$this->generateRefreshScript();
	}
}
 