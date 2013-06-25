<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



class Cluster {

	private $role; /* web, php or proxy */
	private $nodes = array();

	public function __construct($role) {
		$this->role = $role;
	}

	public function addNode(Instance $node) {
		$this->nodes[] = $node;
	}

	private function getRoleColor() {
		static $roles = array(
			'backend' => 'purple',
			'web' => 'blue',
			'proxy' => 'orange',
			'peers' => 'blue',
			'masters' => 'blue',
			'scalaris' => 'blue',
			'slaves' => 'orange',
			'workers' => 'orange',
			'dir' => 'purple',
			'mrc' => 'blue',
			'osd' => 'orange'
		);
		return $roles[$this->role];
	}

	private function getRoleClass() {
		return 'cluster-'.$this->role;
	}

	private function getRole() {
		if ($this->role == 'backend') {
			if (count($this->nodes) > 0) {
				$first = $this->nodes[0];
				if ($first instanceof JavaInstance) {
					return 'java';
				} else if ($first instanceof PHPInstance) {
					return 'php';
				}
			}
		}
		return $this->role;
	}

	public function render() {
		$html =
			'<div class="cluster '.$this->getRoleClass().'">'.
			'<div class="cluster-header">'.
				'<div class="tag '.$this->getRoleColor().'">'.
					$this->getRole().'</div>'.
			'</div>';
		foreach ($this->nodes as $instance) {
			$html .= $instance->renderInCluster();
		}
		$html .= '</div>';
		return $html;
	}

	public function getSize() {
		return count($this->nodes);
	}

}
