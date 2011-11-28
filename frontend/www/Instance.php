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

class Instance {
	
	private $info;
	
	public function __construct($info) {
		$this->info = $info;
	}
	
	private function renderCapabs() {
		$html = '';
		if ($this->info['isRunningProxy']) {
			$html .= '<div class="tag orange">proxy</div>';
		}
		if ($this->info['isRunningWeb']) {
			$html .= '<div class="tag blue">web</div>';
		}
		if ($this->info['isRunningBackend']) {
			$html .= '<div class="tag purple">' . $this->info['service_type'] . '</div>';
		}
		return $html;
	}
	
	public function render() {
		return
		'<div class="instance dualbox">'
			.'<div class="left">'
				.'<i class="title">Instance '.$this->info['id'].'</i>'
				.$this->renderCapabs()
				.'<div class="brief">running</div>'
			.'</div>'
			.'<div class="right">'
				.'<i class="address">'.$this->info['ip'].'</i>'
			.'</div>'
			.'<div class="clear"></div>'
		.'</div>';
	}
	
	public function renderInCluster() {
		return
		'<div class="instance dualbox">'
			.'<div class="left">'
				.'<i class="title">Instance '.$this->info['id'].'</i>'
				.'<i class="timestamp">running for 6 hours</i>'
			.'</div>'
			.'<div class="right">'
				.'<i class="address">'.$this->info['ip'].'</i>'
			.'</div>'
			.'<div class="clear"></div>'
		.'</div>';
	}
	
	public function getSize() {
		return 1;
	}
}

?>
