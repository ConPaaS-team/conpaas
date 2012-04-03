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
			try {
				$serviceUI = new DashboardServiceUI($this->services[$i]);
				if ($i == count($this->services) - 1) {
					$serviceUI->setLast();
				}
				$html .= $serviceUI->__toString();
			} catch (Exception $e) {
				// just skip the bad behaving service and report the exception
				dlog('Exception trying to render the dashboard service UI:'
					.' sid: '.$this->services[$i]->getSID()
					.' error: '.$e->getMessage());
			}
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

	public function render() {
		if (count($this->services) == 0) {
			return
			'<div class="box infobox">'
				.'You have no services in the dashboard. '
				.'Go ahead and <a href="create.php">create a service</a>.'
			.'</div>';
		}
		return
  		'<div class="services">'.
  			'<table class="slist" cellpadding="0" cellspacing="1">'.
				$this->renderItems().
  			'</table>'.
  		'</div>';
	}

	public function toArray() {
		$descr = array();
		foreach ($this->services as $service) {
			$descr []= $service->toArray();
		}
		return $descr;
	}
}
