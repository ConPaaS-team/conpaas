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

function EditableTag() {
	return new EditableTag();
}

class EditableTag extends Tag {

	protected $id = '';
	protected $value = '';
	protected $text = '';

	public function setID($id) {
		$this->id = $id;
		return $this;
	}

	public function setValue($value) {
		$this->value = $value;
		return $this;
	}

	public function setText($text) {
		$this->text = $text;
		return $this;
	}

	protected function renderContent() {
		return
			'<b id="'.$this->id.'" class="editable" title="click to edit">'
			.$this->value.'</b> '.$this->text;
	}
}