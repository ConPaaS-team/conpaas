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

require_once('Instance.php');

class Cluster {
	
	private $role; /* web, php or proxy */
	private $nodes = array();
	
	public function __construct($role, $roleName=NULL) {
		$this->role = $role;
		if ($roleName !== NULL)
		  $this->roleName = $roleName;
		else
		  $this->roleName = $role;
	}
	
	public function addNode($node) {
		$this->nodes[] = $node;
	}
	
	private function getRoleColor() {
		static $roles = array(
			'backend' => 'purple',
			'web' => 'blue',
			'proxy' => 'orange'
		);
		return $roles[$this->role];
	}
	
	private function getRoleClass() {
		return 'cluster-'.$this->role;
	}
	
	public function render() {
		$html =
			'<div class="cluster '.$this->getRoleClass().'">'.
			'<div class="cluster-header">'.
				'<div class="tag '.$this->getRoleColor().'">'.$this->roleName.'</div>'.
			'</div>';
		foreach ($this->nodes as $node) {
			$instance = new Instance($node);
			$html .= $instance->renderInCluster(); 
		}
		$html .= '</div>';
		return $html;
	}

	public function getSize() {
		return count($this->nodes);
	}
	
}

?>
