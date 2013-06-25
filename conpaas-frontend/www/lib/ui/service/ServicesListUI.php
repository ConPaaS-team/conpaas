<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



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
