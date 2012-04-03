<?php
/*
 * Copyright (C) 2010-2012 Contrail consortium.
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