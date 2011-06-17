<?php 

require_once('Service.php');

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