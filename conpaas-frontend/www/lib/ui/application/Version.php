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