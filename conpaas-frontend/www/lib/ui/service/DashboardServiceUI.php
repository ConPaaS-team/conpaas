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
		return
			'<div class="icon">'
				.'<img src="images/'.$this->service->getType().'.png"/>'
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
		$title = 'virtual instance';
		if ($nodes > 1) {
			$title .= 's'; // plural
		}
		return
			$this->renderStatistic(
				'<i class="text">'.$nodes.'</i>'
				.'<img align="top" src="images/server-icon.png" />',
				$title);
	}

	private function renderStats() {
		if (!$this->service->isReachable()) {
			if ($this->service->getState() == Service::STATE_INIT) {
				return $this->renderStatistic(
					'<img src="images/throbber-on-white.gif" />','loading...');
			} else {
				return
				$this->renderStatistic('<img class="deleteService" '.
					'title="delete service" src="images/remove.png" />',
					'').
				$this->renderStatistic(
					'<img src="images/warning.png" />', 'unreachable');
			}
		}
		/* is reachable */
		if ($this->service->getState() == Service::STATE_ERROR) {
			return
				$this->renderStatistic('<img class="deleteService" '
					.'title="delete service" src="images/remove.png" '
					.'name="'.$this->service->getSID()
						.'" onclick="onDeleteService(this);"/>', '')
				.$this->renderStatistic('<img src="images/warning.png" />',
					$this->service->getErrorMessage());
		}
		if ($this->service->getState() == Service::STATE_INIT) {
			return $this->renderInstances();
		}
		$monitor = $this->service->fetchHighLevelMonitoringInfo();

		if ($this->service->getType() == 'php') {
			$resptime =
				'<i class="text">'.$monitor['throughput'].'ms</i>'.
				'<img src="images/green-down.png" />';

			return
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
				$this->renderInstances().
				$this->renderStatistic('<i class="text">'.
					$namenode_data['capacity'].'</i>', 'Total Capacity').
				$this->renderStatistic('<i class="text">'.
					$namenode_data['used'].'</i>', 'Stored Data');
		} else if ($this->service->getType() == 'scalarix') {
			$keysCount = $this->service->getKeysCount();
			return
				$this->renderInstances().
				$this->renderStatistic('<i class="text">'.
					$keysCount.'</i>', 'KeyValue Pairs');
		}
		return $this->renderInstances();
	}

	private function renderColorTag() {
		$color_class = 'colortag-stopped';
		static $active_states = array(
			Service::STATE_RUNNING => true,
			Service::STATE_ADAPTING => true,
		);
		if (array_key_exists($this->service->getState(), $active_states)) {
			$color_class = 'colortag-active';
		}
		return
			'<td class="colortag '.$color_class.'"></td>';
	}

	private function getConfigureEndpoint() {
		return $this->service->getType().'.php';
	}

	private function renderTitle() {
		if (!$this->service->isConfigurable()) {
			$title = $this->service->getName();
		} else {
			$title =
			'<a href="'.$this->getConfigureEndpoint().'?sid='
				.$this->service->getSID().'">'
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
				.$this->renderColorTag()
				.'<td class="wrapper '.$lastClass.'">'
					.$this->renderImage()
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
