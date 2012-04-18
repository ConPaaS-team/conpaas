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

class PhpPage extends HostingPage {

	private $conf = null;

	private function renderSettingsRow($description, $input) {
		return
			'<tr>'
				.'<td class="description">'.$description.'</td>'
				.'<td class="input">'.$input.'</td>'
			.'</tr>';
	}

	private function renderSwVersionInput() {
		return
		'<select onchange="confirm(\'Are you sure you want to change the '
			.' software version?\')">'
	  		.'<option>5.3</option>'
	  	.'</select>';
	}

	private function getCurrentExecLimit() {
		if ($this->conf == null) {
			$this->conf = $this->service->getConfiguration();
		}
		if ($this->conf == null || !isset($this->conf->max_execution_time)) {
			// default value
			return 30;
		}
		return intval($this->conf->max_execution_time);
	}

	public function renderExecTimeOptions() {
		static $options = array(30, 60, 90);
		$selected = $this->getCurrentExecLimit();
		$html = '<select id="conf-maxexec">';
		foreach ($options as $option) {
			$selectedField = $selected == $option ?
				'selected="selected"' : '';
			$html .= '<option value="'.$option.'" '.$selectedField.'>'
				.$option.' seconds</option>';
		}
		$html .= '</select>';
		return $html;
	}

	private function getCurrentMemLimit() {
		if ($this->conf == null) {
			$this->service->getConfiguration();
		}
		if ($this->conf == null || !isset($this->conf->memory_limit)) {
			// default value
			return '128M';
		}
		return $this->conf->memory_limit;
	}

	public function renderMemLimitOptions() {
		static $options = array('64M', '128M', '256M');
		$selected = $this->getCurrentMemLimit();
		$html = '<select id="conf-memlim">';
		foreach ($options as $option) {
			$selectedField = $selected == $option ?
				'selected="selected"' : '';
			$html .= '<option value="'.$option.'" '.$selectedField.'>'
				.$option.'</option>';
		}
		$html .= '</select>';
		return $html;
	}

	public function renderSettingsSection() {
		return
		'<div class="form-section">'
			.'<div class="form-header">'
				.'<div class="title">Settings</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.'<table class="form settings-form">'
				.$this->renderSettingsRow('Software Version ',
					$this->renderSwVersionInput())
				.$this->renderSettingsRow('Maximum script execution time',
					$this->renderExecTimeOptions())
				.$this->renderSettingsRow('Memory limit',
					$this->renderMemLimitOptions())
				.'<tr><td class="description"></td>'
					.'<td class="input actions">'
					.'<input id="saveconf" type="button" disabled="disabled" '
						.'value="save" />'
					 .'<i class="positive invisible">Submitted successfully</i>'
					.'</td>'
				.'</tr>'
			.'</table>'
		.'</div>';
	}

	public function renderContent() {
		return $this->renderInstancesSection()
			.$this->renderCodeSection()
			.$this->renderSettingsSection();
	}
}