<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
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
