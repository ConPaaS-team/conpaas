<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



class ApplicationsListUI {

	private $applications;

	public function __construct(array $applications) {
		$this->applications = $applications;
	}

	public function addApplication(Application $application) {
		$this->applications[] = $application;
		return $this;
	}

	public function isEmpty() {
		return count($this->applications) == 0;
	}

	private function renderItems() {
		$html = '';
		for ($i = 0; $i < count($this->applications); $i++) {
			try {
				$applicationUI = new DashboardApplicationUI($this->applications[$i]);
				if ($i == count($this->applications) - 1) {
					$applicationUI->setLast();
				}
				$html .= $applicationUI->__toString();
			} catch (Exception $e) {
				// just skip the bad behaving service and report the exception
				dlog('Exception trying to render the dashboard application UI:'
					.' sid: '.$this->applications[$i]->getAID()
					.' error: '.$e->getMessage());
			}
		}
		return $html;
	}

	public function needsRefresh() {
		foreach ($this->applications as $application) {
			if ($application->needsPolling()) {
				return true;
			}
		}
		return false;
	}

	public function render() {
		if (count($this->applications) == 0) {
			return
			'<div class="box infobox">'
				.'You have no applications in the dashboard. '
				.'Go ahead and <a id="newapplink" href="#">create a new application</a>.'
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
		foreach ($this->applications as $application) {
			$descr []= $application->toArray();
		}
		return $descr;
	}
}
