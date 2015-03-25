<?php
/* Copyright (C) 2010-2015 by Contrail Consortium. */



require_module('ui');
require_module('logging');

function GenericVolume($data) {
	return new GenericVolume($data);
}

class GenericVolume {

	private $volumeName;
	private $volumeSize;
	private $agentId;
	private $last = false;

	public function __construct($data) {
		$this->volumeName = $data['volumeName'];
		$this->volumeSize = $data['volumeSize'];
		$this->agentId = $data['agentId'];
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

	private function renderVolumeSize() {
		return '<span> &middot; </span>'
			.'size <b>'.$this->volumeSize.'MB</b>';
	}

	private function renderAgentId() {
		return '<span> &middot; </span>'
			.'attached to <b>'.$this->agentId.'</b>';
	}

	private function renderDeleteIcon() {
		return '<img name="'.$this->volumeName.'"'
			.' class="delete" src="images/remove.png">';
	}

	public function __toString() {
		return
			'<tr class="service">'
				.'<td class="'.$this->renderClass().'">'
					.'<div class="content generic-details">'
						.$this->renderVolumeIcon()
						.$this->renderVolumeName()
						.$this->renderVolumeSize()
						.$this->renderAgentId()
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
