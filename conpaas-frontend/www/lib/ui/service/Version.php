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
	private $type;
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
		if (substr($this->name, 0, 4) === 'git-') {
			$this->type = 'git';
		} else {
			$this->type = 'archive';
		}
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

	private function renderLodingGif() {
		return '<img class="loading" align="middle" style="display: none;" '
				.' src="images/icon_loading.gif" />';
	}

	private function renderActivateLink() {
		if ($this->active) {
			return ' &middot; <div class="status active">active</div>';
		}
		return '<span class="dot"> &middot; </span>'
			.'<a class="link activate" href="javascript: void(0);" '
				.' name="'.$this->name.'">'
				.'set active'
			.'</a>';
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
		if ($this->type == 'git') {
			$toolTipText = 'git commit';
			$filename = 'commit '.$this->filename;
		} else {
			$toolTipText = 'file name';
			$filename = $this->filename;
		}
		return
			'<b class="filename" title="'.$toolTipText.'">'.$filename.'</b>';
	}

	private function renderDownloadLink() {
		if ($this->type == 'git') {
			return '';
		}
		return '<span class="dot"> &middot; </span>'
			.'<a href="'.$this->downloadURL.'" '
			.' class="link download" title="download code version archive">'
			.'download</a>';
	}

	private function renderDeleteLink() {
		if (!$this->active) {
			return '<span class="dot"> &middot; </span>'
					.'<a class="link delete" href="javascript: void(0);" '
					.' name="'.$this->name.'">'
					.'delete'
				.'</a>';
		} else {
			return '';
		}
	}

	public function __toString() {
		return
			'<li class="'.$this->renderClass().'">'
			.$this->renderName()
			.$this->renderFilename()
			.'<div class="left version-actions">'
				.$this->renderLodingGif()
				.$this->renderActivateLink()
				.$this->renderDownloadLink()
				.$this->renderDeleteLink()
			.'</div>'
			.'<div class="timestamp">'
				.TimeHelper::timeRelativeDescr($this->timestamp).' ago'
			.'</div>'
			.'</li>';
	}

}
