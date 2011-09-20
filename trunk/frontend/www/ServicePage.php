<?php
  // Copyright (C) 2010-2011 Contrail consortium.
  //
  // This file is part of ConPaaS, an integrated runtime environment 
  // for elastic cloud applications.
  //
  // ConPaaS is free software: you can redistribute it and/or modify
  // it under the terms of the GNU General Public License as published by
  // the Free Software Foundation, either version 3 of the License, or
  // (at your option) any later version.
  //
  // ConPaaS is distributed in the hope that it will be useful,
  // but WITHOUT ANY WARRANTY; without even the implied warranty of
  // MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  // GNU General Public License for more details.
  //
  // You should have received a copy of the GNU General Public License
  // along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.

require_once('logging.php');
require_once('Page.php');
require_once('Instance.php');
require_once('Cluster.php');
require_once('StatusLed.php');
require_once('TimeHelper.php');
require_once('LinkUI.php');
require_once('Service.php');

class ServicePage extends Page {
	
	static $states = array(
		'INIT' => false,
		'RUNNING' => false,
		'PROLOGUE' => true,
		'EPILOGUE' => true,
		'STOPPED' => false 
	);

	private $service;
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
		return 'services/uploadCodeVersion.php?sid='.$this->service->getSID();
	}
	
	public function getState() {
		$json_text = $this->service->fetchState();
		$responseObj = json_decode($json_text);
		if ($responseObj === null) {
			return 'UNREACHABLE';
		}
		if ($responseObj->error != null) {
			throw new Exception('Something went wrong when fetching the state: `'
			.$json_text.'`');
		}
		return $responseObj->result->state;
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
		foreach ($nodesLists as $role => $nodesList) {
			if (count($nodesList) > 1) {
			    if ($role === 'backend')
				  $cluster = new Cluster($role, $this->service->getType());
				else
				  $cluster = new Cluster($role);
				foreach ($nodesList as $node) {
					$info = $this->service->getNodeInfo($node);
					if ($info !== false) {
					    $info['service_type'] = $this->service->getType();
						$cluster->addNode($info);
					}
				}
				$nodes_info[] = $cluster;
			} else {
				/* just one node for this role */
				$info = $this->service->getNodeInfo($nodesList[0]);
				$id = $info['id'];
				if ($info !== false && !array_key_exists($id, $selected)) {
				    $info['service_type'] = $this->service->getType();
					$nodes_info[] = new Instance($info);
					$selected[$id] = true;
				}
			}
		}
		$this->nodes = $nodes_info;
		return $this->nodes;
	}

	public function getNodesCount() {
		$this->getNodes();
		$count = 0;
		foreach ($this->nodes as $node) {
			$count += $node->getSize();
		}
		return $count;
	}
	
	private function renderCloud() {
		static $cloud_providers = array(
			'local' => 'local deployment',
			'ec2' => 'Amazon EC2',
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
			'<div class="brief">'
				.$this->getNodesCount().' running '.$instances_txt
				.' &middot; on '.$this->renderCloud()
			.'</div>'
			.'<div id="instances">';
		
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

	private function renderStateChange() {
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
	
	private function renderSubname() {
		return 
			'<div class="subname">'
				.$this->renderStateChange()
				.' &middot; '
				.LinkUI('service manager', $this->service->getManager())
					->setExternal(true)
				.' &middot; '
				.LinkUI('manager log', 'viewlog.php?sid='.$this->service->getSID())
					->setExternal(true)
			.'</div>';
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
	
	public function renderSettings() {
	  if ($this->service instanceof PHPService)
	    return $this->renderPHPSettings();
	  elseif ($this->service instanceof JavaService)
	    return $this->renderJavaSettings();
	  else
	    throw new Exception('Unknown service type');
	}
	
	private function renderJavaSettings() {
	  return '<div class="box infobox">No modifiable settings.</div>';
	}
	
	private function renderPHPSettings() {
	  $html = <<<EOD
	    <table class="form settings-form">
			<tr>
	  			<td class="description">Software version </td>
	  			<td class="input">
	  				<select onchange="confirm('Are you sure you want to change the software version?')">
	  					<option>5.3</option>
	  				</select>
	  			</td>
	  		</tr>
			<tr>
				<td class="description">Maximum script execution time</td>
				<td class="input">
	              {$this->renderExecTimeOptions()}
				</td>
			</tr>
			<tr>
				<td class="description">Memory limit </td>
				<td class="input">
	              {$this->renderMemLimitOptions()}
				</td>
			</tr>
			<tr>
				<td class="description"></td>
				<td class="input actions">
					<input id="saveconf" type="button" disabled="disabled" value="save" />
					 <i class="positive" style="display: none;">Submitted successfully</i>
				</td>
			</tr>
		</table>
			
		<script type="text/javascript">
		$(document).ready(function() {
			$('#conf-maxexec, #conf-memlim').change(function() {
				$('#saveconf').removeAttr('disabled');
			});

			$('#saveconf').click(function() {
				var phpconf = {};
				phpconf['max_execution_time'] = $('#conf-maxexec').val();
				phpconf['memory_limit'] = $('#conf-memlim').val();
				var params = {};
				params['phpconf'] = phpconf;
				
				$(this).attr('disabled', 'disabled');
				transientRequest({
					url: 'services/sendConfiguration.php?sid=' + sid,
					method: 'post',
					data: params,
					poll: false,
					status: 'Changing PHP configuration...',
					success: function(response) {
					  	$('.settings-form .actions .positive').show();
					  	setTimeout(
							"$('.settings-form .actions .positive').fadeOut();", 
							2000
						);
					},
					error: function(error) {
						$(this).removeAttr('disabled');
						alert('#saveconf.click() error: ' + error);
					}
				});
			});
		});
		</script>
EOD;
		return $html;
	}
	
}
