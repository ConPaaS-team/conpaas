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

function InputButton($text) {
	return new InputButton($text);
}

class InputButton {
	
	protected $id = '';
	protected $text;
	protected $visible = true;
	protected $disabled = false;
	
	public function __construct($text) {
		$this->text = $text;	
	}
	
	public function setVisible($visible) {
		$this->visible = $visible;
		return $this;
	}
	
	public function setId($id) {
		$this->id = $id;
		return $this;
	}
	
	public function setDisabled($disabled) {
		$this->disabled = $disabled;
		return $this;
	}
	
	private function invisibleClass() {
		if ($this->visible) {
			return '';
		}
		return 'invisible';
	}
	
	private function disabledMarker() {
		if ($this->disabled) {
			return ' disabled="disabled" ';
		}
		return '';
	}
	
	public function __toString() {
		return 
			'<input id="'.$this->id.'" type="button" '
			.' class="button '.$this->invisibleClass().'"'
			.' value="'.$this->text.'" '.$this->disabledMarker().'/>';
	}
}
