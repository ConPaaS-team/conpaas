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
			// application manager
			'manager' => 'black',

			// web services (php / java)
			'backend' => 'purple',
			'web' => 'blue',
			'proxy' => 'orange',

			// mysql
			'mysql'=>'orange',
			'glb'=>'blue',

			// xtreemfs
			'dir' => 'purple',
			'mrc' => 'blue',
			'osd' => 'orange',

			// generic
			'master' => 'blue',
			'node'=>'orange',

			// outdated / unused
			'nodes'=>'orange',
			'peers' => 'blue',
			'masters' => 'blue',
			'slaves' => 'orange',
			'workers' => 'orange',
			'scalaris' => 'blue'
		);
		return $roles[$role];
	}

	private function getRoleTagStyle($role) {
		$color = $this->getRoleColor($role);
		return 'color: '.$color.'; border-color: '.$color.';';
	}

	private function getRoleBorderStyle($role) {
		$color = $this->getRoleColor($role);
		return 'background-color: '.$color.';';
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
		} else if ($role == 'manager') {
			return 'Application manager';
		} else {
			return $role;
		}
	}

	public function renderRoleTags() {
		$html = '';
		foreach ($this->roles as $role) {
			$style = $this->getRoleTagStyle($role);
			$html .=
				'<div class="tag" style="'.$style.'">'.
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
		$n = 1;
		foreach ($this->roles as $role) {
			$style = $this->getRoleBorderStyle($role);
			$class = '';
			if ($n == count($this->roles))
				$class .= ' last';

			$html .= '<tr>'.
						'<td class="cluster-border'.$class.'"'.
								' style="'.$style.'">'.
							'&nbsp;'.
						'</td>';
			if ($n == 1) {
				$rowspan = count($this->roles);
				$html .= '<td class="cluster" rowspan="'.$rowspan.'">'.
							$this->renderCluster().
					     '</td>';
			}
			$html .= '</tr>';

			$n++;
		}
		$html .= '</table>';
		return $html;
	}

	public function getSize() {
		return count($this->nodes);
	}

}
