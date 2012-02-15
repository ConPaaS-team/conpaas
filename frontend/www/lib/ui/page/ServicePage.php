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

require_module('logging');
require_module('service');
require_module('ui');
require_module('ui/instance');

class ServicePage extends Page {

	static $states = array(
		'INIT' => false,
		'RUNNING' => false,
		'PROLOGUE' => true,
		'EPILOGUE' => true,
		'STOPPED' => false,
		'ADAPTING' => true,
	);

	protected $service;
	private $conf = null;
	private $nodes = null;

	public function __construct(Service $service) {
		parent::__construct();
		$this->service = $service;
	}

	public function is_transient($state) {
		return
			!array_key_exists($state, self::$states) ||
			(self::$states[$state] == true);
	}

	public function getUploadURL() {
		return 'ajax/uploadCodeVersion.php?sid='.$this->service->getSID();
	}

	public function getState() {
		$state = $this->service->fetchState();
		if ($state === false) {
			return 'UNREACHABLE';
		}
		if (isset($state['error']) && $state['error'] != null) {
			throw new Exception('Something went wrong when fetching the state:`'
				);
		}
		return $state['result']['state'];
	}

	public function renderActions() {
		$startButton = InputButton('start')
			->setId('start');
		$stopButton = InputButton('stop')
			->setId('stop');
		$terminateButton = InputButton('terminate')
			->setId('terminate');

		switch ($this->service->getState()) {
			case Service::STATE_INIT:
				$stopButton->setVisible(false);
				break;
			case Service::STATE_RUNNING:
				$startButton->setVisible(false);
				$terminateButton->setVisible(false);
				break;
			case Service::STATE_STOPPED:
				$stopButton->setVisible(false);
				break;
			default:
		}
		if (!$this->service->isReachable()) {
			$startButton->setVisible(false);
			$stopButton->setVisible(false);
		}

		return $startButton.' '.$stopButton.' '.$terminateButton;
	}

	public function renderStateClass($state) {
		switch ($state) {
			case 'INIT':
			case 'RUNNING':
				return 'active';
			case 'STOPPED':
				return 'stopped';
			default:
				return '';
		}
	}

	private function getVersionDownloadURL($versionID) {
		return $this->service->getManager()
			.'?action=downloadCodeVersion&codeVersionId='.$versionID;
	}

	public function renderVersions() {
		$versions = $this->service->fetchCodeVersions();
		if ($versions === false) {
			return '<h3> No versions available </h3>';
		}
		$active = null;
		for ($i = 0; $i < count($versions); $i++) {
			if (isset($versions[$i]['current'])) {
				$active = $i;
			}
		}
		if (count($versions) == 0) {
			return '<h3> No versions available </h3>';
		}
		$html = '<ul class="versions">';
		for ($i = 0; $i < count($versions); $i++) {
			$versions[$i]['downloadURL'] =
				$this->getVersionDownloadURL($versions[$i]['codeVersionId']);
			$versionUI = Version($versions[$i])
				->setLinkable($this->service->isRunning());
		if ($active == $i) {
		  if ($this->service->isRunning()) {
			$versionUI->setActive(true, $this->service->getAccessLocation());
		  }
		  else {
		    $versionUI->setActive(true);
		  }
		}
			if ($i == count($versions) - 1) {
				$versionUI->setLast();
			}
			$html .= $versionUI;
		}
		$html .= '</ul>';
		return $html;
	}

	private function getCurrentExecLimit() {
		if ($this->conf == null) {
			$this->conf = $this->service->getConfiguration();
		}
		if ($this->conf == null || !isset($this->conf->max_execution_time)) {
			// default value
			return 30;
		}
		return intval($this->conf->max_execution_time);
	}

	public function renderExecTimeOptions() {
		static $options = array(30, 60, 90);
		$selected = $this->getCurrentExecLimit();
		$html = '<select id="conf-maxexec">';
		foreach ($options as $option) {
			$selectedField = $selected == $option ?
				'selected="selected"' : '';
			$html .= '<option value="'.$option.'" '.$selectedField.'>'
				.$option.' seconds</option>';
		}
		$html .= '</select>';
		return $html;
	}

	private function getCurrentMemLimit() {
		if ($this->conf == null) {
			$this->service->getConfiguration();
		}
		if ($this->conf == null || !isset($this->conf->memory_limit)) {
			// default value
			return '128M';
		}
		return $this->conf->memory_limit;
	}

	public function renderMemLimitOptions() {
		static $options = array('64M', '128M', '256M');
		$selected = $this->getCurrentMemLimit();
		$html = '<select id="conf-memlim">';
		foreach ($options as $option) {
			$selectedField = $selected == $option ?
				'selected="selected"' : '';
			$html .= '<option value="'.$option.'" '.$selectedField.'>'
				.$option.'</option>';
		}
		$html .= '</select>';
		return $html;
	}

	public function getNodes() {
		if ($this->nodes !== null) {
			return $this->nodes;
		}
		$nodes = array();
		$nodes_info = array();
		$selected = array();
		$nodesLists = $this->service->getNodesLists();
		if ($this->service->hasDedicatedManager()) {
			$nodes_info[] = new ManagerInstance(
				$this->service->getManagerVirtualID(),
				$this->service->getManagerIP()
			);
		}
		$roles = $this->service->getInstanceRoles();
		if ($roles === false) {
			$roles = array_keys($nodesLists);
		}
		foreach ($roles as $role) {
			if (!isset($nodesLists[$role])) {
				continue;
			}
			$nodesList = $nodesLists[$role];
			if (count($nodesList) > 1) {
				$cluster = new Cluster($role);
				foreach ($nodesList as $node) {
					$info = $this->service->getNodeInfo($node);
					if ($info !== false) {
						$cluster->addNode($this->service->createInstanceUI(
							$node));
					}
				}
				$nodes_info[] = $cluster;
			} else {
				/* just one node for this role */
				$node = $nodesList[0];
				$info = $this->service->getNodeInfo($node);
				$id = $info['id'];
				if ($info !== false && !array_key_exists($id, $selected)) {
					$nodes_info[] = $this->service->createInstanceUI($node);
					$selected[$id] = true;
				}
			}
		}
		$this->nodes = $nodes_info;
		return $this->nodes;
	}

	private function renderCloud() {
		static $cloud_providers = array(
			'local' => 'local deployment',
			'ec2' => 'Amazon EC2',
			'opennebula' => 'OpenNebula',
		);
		return $cloud_providers[$this->service->getCloud()];
	}

	public function renderInstances() {
		$nodes = $this->getNodes();
		if ($nodes === false) {
			return 'could not retrieve nodes';
		}
		$instances_txt = count($nodes) > 1 ? 'instances' : 'instance';
		$html =
			'<div class="brief">'.
				$this->service->getNodesCount().' '.$instances_txt.' running '.
				'on '.$this->renderCloud().
			'</div>'.
			'<div id="instances">';

		foreach ($nodes as $node) {
			$html .= $node->render();
		}
		$html .= '</div>';
		return $html;
	}

	private function getTypeImage() {
		return $this->service->getType().'.png';
	}

	private function renderEditableName() {
		if (!$this->service->isConfigurable()) {
			return '<i class="name">'.$this->service->getName().'</i>';
		}
		return
			'<i id="name" class="name editable" title="click to edit">'
				.$this->service->getName()
			.'</i>';
	}

	protected function renderStateChange() {
		$stateLog = $this->service->fetchStateLog();
		// consider state changes in reverse order
		foreach (array_reverse($stateLog) as $stateChange) {
			if (Service::stateIsStable($stateChange['state'])) {
				$ts = TimeHelper::timeRelativeDescr($stateChange['time']);
				$state = ($stateChange['state'] == 'RUNNING') ?
					'started' : strtolower($stateChange['state']);
				return $state.' '.$ts.' ago';
			}
		}
		// default
		$ts = TimeHelper::timeRelativeDescr(
			strtotime($this->service->getDate()));
		return 'created '.$ts.' ago';
	}

	protected function renderApplicationAccess() {
		if (!$this->service->isRunning()) {
			return '';
		}
		return ' &middot; '.
			LinkUI('access application', $this->service->getAccessLocation())
				->setExternal(true);
	}

	protected function renderSubname() {
		return
			'<div class="subname">'.
				$this->renderStateChange().
				$this->renderApplicationAccess().
				' &middot; '.
				LinkUI('manager log',
						'viewlog.php?sid='.$this->service->getSID())
					->setExternal(true).
			'</div>';
	}

	private function renderName() {
		return
			'<div class="nameWrapper">'
				.$this->renderEditableName()
				.$this->renderSubname()
			.'</div>';
	}

	public function renderTopMenu() {
		return
    	'<div class="pageheader">'
    		.'<div class="info">'
    			.'<img class="stype" '
    				.' src="images/'.$this->getTypeImage().'" />'
    			.$this->renderName()
    		.'</div>'
	  		.'<div class="menu">'
	  			.StatusLed($this->service)
	  			.$this->renderActions()
	  		.'</div>'
	  		.'<div class="clear"></div>'
	  	.'</div>';
	}

}
