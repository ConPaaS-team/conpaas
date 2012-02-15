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

function CloudOption($cloud, $title) {
	return new CloudOption($cloud, $title);
}

class CloudOption {

	private $cloud;
	private $title;
	private $enabled = true;
	private $selected = false;

	public function __construct($cloud, $title) {
		$this->cloud = $cloud;
		$this->title = $title;
	}

	public function setEnabled($enabled) {
		$this->enabled = $enabled;
		return $this;
	}

	public function setSelected($selected) {
		$this->selected = $selected;
		return $this;
	}

	private function disabledMarker() {
		if ($this->enabled) {
			return '';
		}
		return ' disabled="disabled" ';
	}

	private function selectedMarker() {
		if (!$this->selected) {
			return '';
		}
		return ' selected="selected" ';
	}

	public function __toString() {
		return '<option value="'.$this->cloud.'" '
			.$this->disabledMarker().$this->selectedMarker().'>'
			.$this->title.'</option>';
	}

}