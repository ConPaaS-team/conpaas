<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



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
