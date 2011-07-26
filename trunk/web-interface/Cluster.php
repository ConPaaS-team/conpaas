<?php 

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
