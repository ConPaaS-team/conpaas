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
			'workers' => 'orange'
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
