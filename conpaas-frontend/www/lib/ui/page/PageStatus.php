<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



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
