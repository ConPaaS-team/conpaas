<?php 

require_once('ServiceItem.php');
require_once('ServiceFactory.php');

class ServicesListUI {
	
	private $services;
	
	public function __construct(array $services) {
		$this->services = array();
		foreach ($services as $service_data) {
			$this->services[] = ServiceFactory::createInstance($service_data);
		}
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
			$serviceUI = new ServiceItem($this->services[$i]);
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
