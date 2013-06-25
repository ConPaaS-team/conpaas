<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



function InputButton($text) {
    return new InputButton($text);
}

class InputButton extends Button {

    public function __construct($text) {
        parent::__construct($text);
    }

    public function __toString() {
        return
            '<input id="'.$this->id.'" type="button" '
            .' title="'.$this->title.'"'
            .' class="button '.$this->isVisible().'"'
            .' value="'.$this->text.'" '.$this->disabledMarker().'/>';
    }
}
