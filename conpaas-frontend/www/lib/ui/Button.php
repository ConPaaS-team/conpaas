<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */




class Button{

    protected $id = '';
    protected $text;
    protected $visible = true;
    protected $disabled = false;
    protected $title= '';

    public function __construct($text) {
        $this->text = $text;
    }

    public function setVisible($visible) {
        $this->visible = $visible;
        return $this;
    }

    public function isVisible() {
        return $this->visible ? '' : 'invisible';
    }

    public function setId($id) {
        $this->id = $id;
        return $this;
    }

    public function setDisabled($disabled) {
        $this->disabled = $disabled;
        return $this;
    }

    public function setTitle($title) {
        $this->title = $title;
        return $this;
    }

    protected function disabledMarker() {
        if ($this->disabled) {
            return ' disabled="disabled" ';
        }
        return '';
    }
}
