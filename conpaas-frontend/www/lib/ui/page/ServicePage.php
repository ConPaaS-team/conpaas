<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



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
		$app = LinkUI('Dashboard', 'index.php')
			->setIconPosition(LinkUI::POS_LEFT)
			->setIconURL('images/link_s_back.png');
		$dashboard = LinkUI('This application', 'application.php?aid='.$_SESSION['aid'])
			->setIconPosition(LinkUI::POS_LEFT)
			->setIconURL('images/link_s_back.png');

		return $app . $dashboard;
	}

	public function renderActions() {
		$startButton = InputButton('start')
			->setId('start');
		$stopButton = InputButton('stop')
			->setId('stop');
		$removeButton = InputButton('remove')
			->setId('remove');

        $clouds = json_decode(HTTPS::get(Conf::DIRECTOR . '/available_clouds'));
        $selectedCloud = $this->service->getApplication()->getCloud();
        if ($selectedCloud === 'iaas') {
            $selectedCloud = 'default';
        }
        $radios = '';
        foreach($clouds as $cloud){
            $radio = Radio($cloud);
            $radio->setTitle("available_clouds");

            if ($cloud === $selectedCloud) {
                $radio->setDefault();
            }
            if ($cloud === 'default') {
                $radios = $radio;
            } else {
                $radios = $radios.'<br>'.$radio;
            }
        }
        $cloudChoice = Tag();
        $cloudChoice->setHTML($radios);

		$serviceSelection = '';
		$serviceSelector = $this->renderServiceSelection();
		if ($serviceSelector != '') {
				$serviceSelection = Tag();
				$serviceSelection->setHTML($serviceSelector);
		}

		switch ($this->service->getState()) {
			case Service::STATE_INIT:
				$stopButton->setVisible(false);
				break;
			case Service::STATE_RUNNING:
				$startButton->setVisible(false);
				$removeButton->setVisible(false);
					if ($serviceSelector != '') {
							$serviceSelection->setVisible(false);
					}
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

		return $startButton.' '.$stopButton.' '.$removeButton.' '.$cloudChoice.$serviceSelection;
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
		// If we already have the list of nodes, do not compute it again
		if ($this->nodes !== null) {
			return $this->nodes;
		}

		$nodesInfo = array(); // final list
		$selected = array(); // nodes that are already added to it
		$nodesLists = $this->service->getNodesLists();

		// Get the list of roles
		$roles = $this->service->getInstanceRoles();
		if ($roles === false) {
			$roles = array_keys($nodesLists);
		} else {
			// Make sure we don't use roles which are not currently present
			$roles = array_intersect($roles, array_keys($nodesLists));
		}

		// Get the list of nodes
		$nodes = array();
		foreach ($roles as $role) {
			$nodes = array_merge($nodes, $nodesLists[$role]);
		}
		$nodes = array_unique($nodes);

		// For each node, if it has more than one role, add it separately
		foreach ($nodes as $node) {
			$nodeRoles = array();
			foreach ($roles as $role) {
				if (in_array($node, $nodesLists[$role])) {
					$nodeRoles[] = $role;
				}
			}
			if (count($nodeRoles) > 1) {
				$info = $this->service->getNodeInfo($node);
				if ($info !== false) {
					$cluster = new Cluster($nodeRoles);
					$cluster->addNode($this->service->createInstanceUI($node));
					$nodesInfo[] = $cluster;
				}
				$selected[$node] = true;
			}
		}

		// For each role, get the remaining nodes (that were not added already)
		foreach ($roles as $role) {
			$remainingNodes = array();
			foreach ($nodesLists[$role] as $node) {
				if (!array_key_exists($node, $selected)) {
					$info = $this->service->getNodeInfo($node);
					if ($info !== false) {
						$remainingNodes[] = $node;
					}
				}
			}
			if (count($remainingNodes) > 0) {
				// We add all these nodes together in a cluster
				$cluster = new Cluster(array($role));
				foreach ($remainingNodes as $node) {
					$cluster->addNode($this->service->createInstanceUI($node));
				}
				$nodesInfo[] = $cluster;
			}
		}

		// Store the final list and return it
		$this->nodes = $nodesInfo;
		return $this->nodes;
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
				'in '.$this->service->getCloudName().
			'</div>'.
			'<div id="instances">';

		foreach ($nodes as $node) {
			$html .= $node->render();
		}
		$html .= '</div>';
		return $html;
	}

	protected function getTypeImage() {
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
				return 'since '.$ts.' ago';
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
						'viewlog.php?aid='.$this->service->getAID()
				                  .'&sid='.$this->service->getSID())
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
    				.' src="images/'.$this->getTypeImage().'" height="32" />'
    			.$this->renderName()
    		.'</div>'
			.$this->renderRightMenu()
	  		.'<div class="clear"></div>'
	  	.'</div>';
	}

        protected function renderServiceSelection() {
                return '';
        }

	protected function renderInstanceActions() {
		return '';
	}

        protected function renderIncompleteGUI() {
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

    public function renderStartupScriptSection() {
		return
        '<div class="form-section">'
        .'<div class="form-header">'
            .'<div class="title">Startup script</div>'
            .'<div class="clear"></div>'
        .'</div>'
		.'<div class="actionsbar">'
           .'<textarea id="startupscript" cols="94" rows="5" name="startupscript"></textarea><br />'
           .'<div class="additionalStartup">'
           .'<img class="loading invisible" '
               .' src="images/icon_loading.gif" />'
           .'<i class="uploadStatus invisible"></i>'
           .'</div>'
           .'<div class="clear"></div>'
           .'<div class="hint">'
           .'Paste your startup script'
           .'</div>'
           .'<button id="submitStartupScript">Submit script</button>'
		.'</div></div>';
    }

	public function renderInstancesSection() {
		if ($this->service->getNodesCount() == 0) {
			return '<div class="box infobox">No instances are running</div>';
		}
		return
			'<div class="form-section">'
				.'<div id="instancesWrapper">'
					.$this->renderInstances()
				.'</div>'
				.$this->renderInstanceActionsSection()
                                .$this->renderIncompleteGUI()
			.'</div>';
	}
}
