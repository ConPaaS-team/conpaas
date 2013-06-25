<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('application');
require_module('ui');

function DashboardApplicationUI(Application $application) {
	return new DashboardApplicationUI($application);
}

class DashboardApplicationUI {

	private $application;
	private $last = false;

	public function __construct(Application $application) {
		$this->application = $application;
	}

	public function setLast($last=true) {
		$this->last = $last;
		return $this;
	}

	private function renderStatistic($content) {
		return
			'<div class="statistic">'
				.'<div class="statcontent">'.$content.'</div>'
			.'</div>';
	}

    private function renderStats() {
        return $this->renderStatistic('<img class="deleteApplication-'.
            $this->application->getAID().'" src="images/remove.png" />');
    }

	private function renderTitle() {
		$title =
			'<a href="services.php?aid='.$this->application->getAID().'">'
			.$this->application->getName()
			.'</a>';

		return
			'<div class="title">'
				.$title
			.'</div>';
	}

	public function __toString() {
		$lastClass = $this->last ? 'last' : '';
		return
			'<tr class="service" id="service-'.$this->application->getAID().'">'
				.'<td class="wrapper '.$lastClass.'">'
					.'<div class="content">'
						.$this->renderTitle()
					.'</div>'
					.$this->renderStats()
					.'<div class="clear"></div>'
				.'</td>'
			.'</tr>';
	}

}
