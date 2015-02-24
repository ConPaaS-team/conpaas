<?php
/* Copyright (C) 2010-2015 by Contrail Consortium. */



require_module('ui');
require_module('logging');

function XtreemFSVolume($data) {
	return new XtreemFSVolume($data);
}

class XtreemFSVolume {

	private $volumeName;
	private $volumeUUID;
	private $last = false;

	public function __construct($data) {
		$this->volumeName = $data['volumeName'];
		$this->volumeUUID = $data['volumeUUID'];
	}

	public function setLast() {
		$this->last = true;
		return $this;
	}

	private function renderClass() {
		$class = 'wrapper';
		if ($this->last) {
			$class .= ' last';
		}
		return $class;
	}

	private function renderVolumeIcon() {
		return '<img src="images/volume.png">&nbsp;&nbsp;';
	}

	private function renderVolumeName() {
		return '<b>'.$this->volumeName.'</b>';
	}

	private function renderVolumeUUID() {
		return '<span> &middot; </span>'
			.'UUID <b>'.$this->volumeUUID.'</b>';
	}

	private function renderDeleteIcon() {
		return '<img name="'.$this->volumeName.'"'
			.' class="delete" src="images/remove.png">';
	}

	public function __toString() {
		return
			'<tr class="service">'
				.'<td class="'.$this->renderClass().'">'
					.'<div class="content xtreemfs-details">'
						.$this->renderVolumeIcon()
						.$this->renderVolumeName()
						// .$this->renderVolumeUUID()
					.'</div>'
					.'<div class="statistic">'
						.'<div class="statcontent">'
							.$this->renderDeleteIcon()
						.'</div>'
					.'</div>'
					.'<div class="clear"></div>'
				.'</td>'
			.'</tr>';
	}

}
