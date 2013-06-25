<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



function Radio($text) {
    return new Radio($text);
}

class Radio extends Button{

    protected $checked = '';

    public function setDefault() {
        $this->checked = 'checked';
        return $this;
    }

    public function __construct($text) {
        parent::__construct($text);
    }

    public function __toString() {
        return
            '<input id="'.$this->id.'" type="radio" '
            .' title="'.$this->title.'"'.' name="'.$this->title.'"'
            ." $this->checked"
            .' class="button '.$this->isVisible().'"'
            .' value="'.$this->text.'" '.$this->disabledMarker().'/>'.$this->text;
    }
}
