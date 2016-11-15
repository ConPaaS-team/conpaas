<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */


require_module('ui');


class Cluster {

	private $serviceType;
	private $roles; /* array of roles (web, backend, proxy etc.) */
	private $nodes = array();

	public function __construct($serviceType, $roles) {
		$this->serviceType = $serviceType;
		$this->roles = $roles;
	}

	public function addNode(Instance $node) {
		$this->nodes[] = $node;
	}

	public function renderRoleTags() {
		$html = '';
		foreach ($this->roles as $role) {
			$html .= Tag()
				->setColor(Role::getColor($this->serviceType, $role))
				->setHTML(Role::getText($this->serviceType, $role))
				->setTooltip(Role::getInfo($this->serviceType, $role));
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
			'<div class="cluster">'.
				'<div class="cluster-header">'.
					$this->renderRoleTags().
				'</div>'.
				$this->renderInstanceList().
			'</div>';
	}

	public function renderClusterWithBorder() {
		$html = '<table class="cluster-table" cellspacing="0" cellpadding="0">';
		$n = 1;
		foreach ($this->roles as $role) {
			$color = Role::getColor($this->serviceType, $role);
			$style = 'background-color: '.$color.';';
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
				$html .= '<td rowspan="'.$rowspan.'">'.
							$this->renderCluster().
					     '</td>';
			}
			$html .= '</tr>';

			$n++;
		}
		$html .= '</table>';
		return $html;
	}

	public function render() {
		if (count($this->roles) == 1 && $this->roles[0] === 'manager') {
			return $this->renderCluster();
		} else {
			return $this->renderClusterWithBorder();
		}
	}

	public function getSize() {
		return count($this->nodes);
	}

}
