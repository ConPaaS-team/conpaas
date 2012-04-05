<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
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
	private $nodes = null;

	public function __construct(Service $service) {
		parent::__construct();
		$this->service = $service;
		$this->addJS('js/servicepage.js');
	}

	public function is_transient($state) {
		return
			!array_key_exists($state, self::$states) ||
			(self::$states[$state] == true);
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

	protected function renderBackLinks() {
		return LinkUI('back to Dashboard', 'index.php')
			->setIconPosition(LinkUI::POS_LEFT)
			->setIconURL('images/link_s_back.png');
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

	public function getNodes() {
		if ($this->nodes !== null) {
			return $this->nodes;
		}
		$nodes = array();
		$nodes_info = array();
		$selected = array();
		$nodesLists = $this->service->getNodesLists();
		if ($this->service->hasDedicatedManager()) {
			$manager = $this->service->getManagerInstance();
			$nodes_info[] = new ManagerInstance($manager->getID(),
				$manager->getHostAddress());
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
			// HACK: empty list for a role
			if (count($nodesList) == 0) {
				continue;
			} elseif (count($nodesList) > 1) {
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
		return '<div class="instancesWrapper">'.$html.'</div>';
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
		return '';
	}

	protected function renderRightMenu() {
		return
			'<div class="rightmenu">'.
				$this->renderApplicationAccess().
				LinkUI('manager log',
						'viewlog.php?sid='.$this->service->getSID())
					->setExternal(true).
			'</div>';
	}

	private function renderName() {
		return
			'<div class="nameWrapper">'
				.$this->renderEditableName()
				.$this->renderActions()
				.'<div class="actions">'
					.StatusLed($this->service).' '
					.$this->service->getStatusText()
					.' &middot; '.$this->renderStateChange()
				.'</div>'
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
			.$this->renderRightMenu()
	  		.'<div class="clear"></div>'
	  	.'</div>';
	}

	protected function renderInstanceActions() {
		return '';
	}

	private function renderInstanceActionsSection() {
		if (!$this->service->isRunning()) {
			return '';
		}
		return
		'<div class="actionstitle">'
			.'add or remove instances to your deployment'
		.'</div>'
		.'<div class="actionsbar">'
			.$this->renderInstanceActions()
			.'<input type="button" id="submitnodes" value="submit" '
				.' disabled="disabled" />'
			.'<img class="loading invisible" '
				.'src="images/icon_loading.gif" />'
		.'</div>';
	}

	public function renderInstancesSection() {
		if ($this->service->getNodesCount() == 0) {
			return '<div class="box infobox">No instances are running</div>';
		}
		return
			'<div class="form-section">'
				.$this->renderInstances()
				.$this->renderInstanceActionsSection()
			.'</div>';
	}
}
