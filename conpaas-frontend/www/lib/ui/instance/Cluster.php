<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



class Cluster {

	private $roles; /* array of roles (web, php, proxy etc.) */
	private $nodes = array();

	public function __construct($roles) {
		$this->roles = $roles;
	}

	public function addNode(Instance $node) {
		$this->nodes[] = $node;
	}

	private function getRoleColor($role) {
		static $roles = array(
			'node'=>'orange',
			'nodes'=>'orange',
			'backend' => 'purple',
			'web' => 'blue',
			'proxy' => 'orange',
			'peers' => 'blue',
			'master' => 'blue',
			'masters' => 'blue',
			'scalaris' => 'blue',
			'slaves' => 'orange',
			'workers' => 'orange',
			'mysql'=>'orange',
			'glb'=>'blue',
			'dir' => 'purple',
			'mrc' => 'blue',
			'osd' => 'orange'
		);
		return $roles[$role];
	}

	private function getRoleClass($role) {
		return 'cluster-'.$role;
	}

	private function getRoleText($role) {
		if ($role == 'backend') {
			if (count($this->nodes) > 0) {
				$first = $this->nodes[0];
				if ($first instanceof JavaInstance) {
					return 'java';
				} else if ($first instanceof PHPInstance) {
					return 'php';
				}
			}
		} else if ($role == 'dir' || $role == 'mrc' || $role == 'osd') {
			return strtoupper($role);
		} else {
			return $role;
		}
	}

	public function renderRoleTags() {
		$html = '';
		foreach ($this->roles as $role) {
			$html .=
				'<div class="tag '.$this->getRoleColor($role).'">'.
					$this->getRoleText($role).
				'</div>';
		}
		return $html;
	}

	public function renderInstanceList() {
		$html = '';
		foreach ($this->nodes as $instance) {
			$html .= $instance->renderInCluster();
		}
		return $html;
	}

	public function renderCluster() {
		return
			'<div class="cluster-header">'.
				$this->renderRoleTags().
			'</div>'.
			$this->renderInstanceList();
	}

	public function render() {
		$html = '<table class="cluster-table" cellspacing="0" cellpadding="0">';
		$first = true;
		foreach ($this->roles as $role) {
			$html .= '<tr>';
			$html .= '<td class="cluster-border '.$this->getRoleClass($role).'">'.
						'&nbsp;'.
					 '</td>';
			if ($first) {
				$html .= '<td class="cluster" rowspan="'.count($this->roles).'">'.
							$this->renderCluster().
					     '</td>';
				$first = false;
			}
			$html .= '</tr>';
		}
		$html .= '</table>';
		return $html;
	}

	public function getSize() {
		return count($this->nodes);
	}

}
