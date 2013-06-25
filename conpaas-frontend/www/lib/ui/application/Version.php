<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui');
require_module('logging');

function Version($data) {
	return new Version($data);
}

class Version {

	private $name;
	private $filename;
	private $timestamp;
	private $downloadURL =  '';
	private $active = false;
	private $linkAddress = true;
	private $address = null;
	private $last = false;

	public function __construct($data) {
		$this->name = $data['codeVersionId'];
		$this->timestamp = $data['time'];
		$this->filename = $data['filename'];
		$this->downloadURL = $data['downloadURL'];
	}

	public function setLast() {
		$this->last = true;
		return $this;
	}

	public function setActive($active, $address=null) {
		$this->active = $active;
		$this->address = $address;
		return $this;
	}

	public function setLinkable($linkable) {
		$this->linkAddress = $linkable;
		return $this;
	}

	private function renderClass() {
		$class = $this->active ? 'active' : 'inactive';
		if ($this->last) {
			$class .= ' last';
		}
		return $class;
	}

	private function renderActivateLink() {
		$dot = ' &middot; ';
		if ($this->active) {
			return $dot.'<div class="status active">active</div>';
		}
		return
			$dot
			.'<a class="link activate" href="javascript: void(0);" '
				.' name="'.$this->name.'">'
				.'set active'
			.'</a>'
			.'<img class="loading" align="middle" style="display: none;" '
				.' src="images/icon_loading.gif" />';
	}

	private function renderName() {
		if (!$this->active || !$this->linkAddress) {
			return $this->name;
		}

		return LinkUI($this->name, $this->address)
			->setExternal(true)
			->addClass('address');
	}

	private function renderFilename() {
		return
			'<b class="filename" title="filename">'.$this->filename.'</b>';
	}

	private function renderDownloadLink() {
		return
			' &middot; <a href="'.$this->downloadURL.'" '
			.' class="link" title="download code version archive">download</a>';
	}

	public function __toString() {
		return
			'<li class="'.$this->renderClass().'">'
			.$this->renderName()
			.$this->renderFilename()
			.'<div class="left version-actions">'
				.$this->renderActivateLink()
				.$this->renderDownloadLink()
			.'</div>'
			.'<div class="timestamp">'
				.TimeHelper::timeRelativeDescr($this->timestamp).' ago'
			.'</div>'
			.'</li>';
	}

}
