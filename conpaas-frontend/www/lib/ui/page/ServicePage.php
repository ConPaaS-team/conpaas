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
		$app = LinkUI('Applications', 'index.php')
			->setIconPosition(LinkUI::POS_LEFT)
			->setIconURL('images/link_s_back.png');
		$dashboard = LinkUI('Services', 'services.php?aid='.$_SESSION['aid'])
			->setIconPosition(LinkUI::POS_LEFT)
			->setIconURL('images/link_s_back.png');

		return $app . $dashboard;
	}

	public function renderActions() {
		$startButton = InputButton('start')
			->setId('start');
		$stopButton = InputButton('stop')
			->setId('stop');
		$terminateButton = InputButton('terminate')
			->setId('terminate');

        $clouds = json_decode(HTTPS::get(Conf::DIRECTOR . '/available_clouds'));
        $radios = '';
        foreach($clouds as $cloud){
            $radio = Radio($cloud);
            $radio->setTitle("available_clouds");

            if ($cloud === 'default')
                $radio->setDefault();

            $radios = $radios.$radio;
        }
        $cloudChoice = Tag();
        $cloudChoice->setHTML($radios);

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

		return $startButton.' '.$stopButton.' '.$terminateButton.' '.$cloudChoice;
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
    				.' src="images/'.$this->getTypeImage().'" height="32" />'
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

    public function renderStartupScriptSection() {
		return
        '<div class="form-section">'
        .'<div class="form-header">'
            .'<div class="title">Startup script</div>'
            .'<div class="clear"></div>'
        .'</div>'
		.'<div class="actionsbar">'
           .'<textarea id="startupscript" cols="50" rows="5" name="startupscript"></textarea><br />'
           .'<div class="additionalStartup">'
           .'<img class="loading invisible" '
               .' src="images/icon_loading.gif" />'
                                .'<i class="positive invisible">Submitted successfully</i>'
           .'<i class="error invisible"></i>'
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
				.$this->renderInstances()
				.$this->renderInstanceActionsSection()
			.'</div>';
	}
}
