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

function PageStatus() {
	return new PageStatus();
}

class PageStatus {
	
	private $id = '';
	
	public function setId($id) {
		$this->id = $id;
		return $this;
	}
	
	public function __toString() {
		return
		 '<div id="'.$this->id.'" class="loadingWrapper invisible">'
		 	.'<b>loading...</b>'
		  	.'<img class="loading" src="images/throbber-on-white.gif" />'
		 .'</div>';
	}
}
