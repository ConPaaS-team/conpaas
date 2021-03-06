<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



date_default_timezone_set('UTC');
require_module('service');
require_module('ui');

function DashboardServiceUI(Service $service) {
	return new DashboardServiceUI($service);
}

class DashboardServiceUI {

	private $service;
	private $last = false;

	public function __construct(Service $service) {
		$this->service = $service;
	}

	public function setLast($last=true) {
		$this->last = $last;
		return $this;
	}

	private function renderImage() {
		$filename = $this->service->getType().'.png';
		

		return
			'<div class="icon">'
				.'<img src="images/'.$filename.'" height="60" />'
			.'</div>';
	}

	private function renderActions() {
		if (!$this->service->isReachable()) {
			$actions = 'service is unreachable';
			if ($this->service->getState() == Service::STATE_INIT) {
				$actions .= ': <b>initializing</b>';
			}
		} else {
			$ts = strtotime($this->service->getDate());
			$actions = 'created '.TimeHelper::timeRelativeDescr($ts).' ago';
		}

		return
			'<div class="actions">'
				.$actions
			.'</div>';
	}

	private function renderStatistic($content, $note) {
		return
			'<div class="statistic">'
				.'<div class="statcontent">'.$content.'</div>'
				.'<div class="note">'.$note.'</div>'
			.'</div>';
	}

	private function renderInstances() {
		$nodes = $this->service->getNodesCount();
		if ($nodes === 0) {
			return '';
		}
		$title = 'instance';
		if ($nodes > 1) {
			$title .= 's'; // plural
		}
		$title .= ' running';
		return
			$this->renderStatistic(
				'<i class="text">'.$nodes.'</i>'
				.'<img align="top" src="images/server-icon.png" style="margin-top: 5px;" />',
				$title);
	}

		private function renderStats() {
		$delete= '<img class="deleteService" id="delete-'.$this->service->getSID().'" '.
					'title="delete service" src="images/remove.png" style="margin-top: 12px;" />';

		if (!$this->service->isReachable()) {
			if ($this->service->getState() == Service::STATE_INIT) {
				return $this->renderStatistic(
					'<img src="images/throbber-on-white.gif" />','loading...');
			} else {
				return
				$this->renderStatistic($delete,'').
				$this->renderStatistic(
					'<img src="images/warning.png" />', 'unreachable');
			}
		}
		if (!$this->service->isStable()) {
			return $this->renderStatistic(
				'<img src="images/throbber-on-white.gif" />','loading...');
		}
		/* is reachable */
		if ($this->service->getState() == Service::STATE_ERROR) {
			return
				$this->renderStatistic($delete
					.'name="'.$this->service->getSID()
						.'" onclick="onDeleteService(this);"/>', '')
				.$this->renderStatistic('<img src="images/warning.png" />',
					$this->service->getErrorMessage());
		}
		if ($this->service->getState() == Service::STATE_INIT) {
			return $this->renderStatistic($delete,'') . $this->renderInstances();
		}
		$monitor = $this->service->fetchHighLevelMonitoringInfo();

		if ($this->service->getType() == 'php<monitoring-disabled>') {
			$resptime =
				'<i class="text">'.$monitor['throughput'].'ms</i>'.
				'<img src="images/green-down.png" />';

			return
			    $this->renderStatistic($delete,'') .
				$this->renderInstances().
				$this->renderStatistic(
					'<i class="text">'
						.$monitor['error_rate'].'%'
					.'</i> <img src="images/red-up.png" />',
					'error rate').
				$this->renderStatistic(
					'<i class="text">'.$monitor['request_rate'].'/s'
					.'</i> <img src="images/blue-up.png" />',
					'requests rate').
				$this->renderStatistic($resptime, 'response time');
		} else if ($this->service->getType() == 'hadoop') {
			$namenode_data = $this->service->getNamenodeData();
			return
			    $this->renderStatistic($delete,'') .
				$this->renderInstances().
				$this->renderStatistic('<i class="text">'.
					$namenode_data['capacity'].'</i>', 'Total Capacity').
				$this->renderStatistic('<i class="text">'.
					$namenode_data['used'].'</i>', 'Stored Data');
		} else if ($this->service->getType() == 'scalaris') {
			return $this->renderStatistic($delete,'') . $this->renderInstances();
		}
		return $this->renderStatistic($delete ,'').$this->renderInstances();
	}

	private function renderTitle() {
		if (!$this->service->isConfigurable()) {
			$title = $this->service->getName();
		} else {
			$title =
			'<a href="service.php?'
						.'aid='.$this->service->getAID().'&'
						.'sid='.$this->service->getSID()
						.'">'
				.$this->service->getName()
			.'</a>';
		}
		return
			'<div class="title">'
				.$title
				.StatusLed($this->service)
			.'</div>';
	}

	public function __toString() {
		$lastClass = $this->last ? 'last' : '';
		return
			'<tr class="service" id="service-'.$this->service->getSID().'">'
				.ColorTag($this->service->getState())
				.'<td class="wrapper-left '.$lastClass.'">'
					.$this->renderImage()
				.'</td>'
				.'<td class="wrapper-right '.$lastClass.'">'
					.'<div class="content">'
						.$this->renderTitle()
						.$this->renderActions()
					.'</div>'
					.$this->renderStats()
					.'<div class="clear"></div>'
				.'</td>'
			.'</tr>';
	}

}
