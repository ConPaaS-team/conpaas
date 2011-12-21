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

function LinkUI($text, $href) {
	return new LinkUI($text, $href);
}

class LinkUI {
	
	private $text;
	private $href;
	private $external = false;
	private $class = 'link';
	private $iconURL = 'images/link_s.png';
	
	public function __construct($text, $href) {
		$this->text = $text;
		$this->href = $href;
	}
	
	public function setExternal($external) {
		$this->external = $external;
		return $this;
	}
	
	public function setIconURL($url) {
		$this->iconURL = $url;
		return $this;
	}
	
	public function addClass($class) {
		$this->class .= ' '.$class;
		return $this;
	}
	
	private function renderSymbol() {
		return 
			'<img src="'.$this->iconURL.'" style="vertical-align: middle;" />';
	}
	
	public function __toString() {
		$target = $this->external ? 'target="new"' : '';
		return
		'<div class="'.$this->class.'">'
			.'<a href="'.$this->href.'" '.$target.'>'.$this->text.'</a>'
			.$this->renderSymbol()
		.'</div>';
	}
}
 