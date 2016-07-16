<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



function Tag () {
    return new Tag();
}

class Tag {

    protected $color = 'blue';
    protected $visible = '';
    protected $tooltip = '';
    private $html = '';

    public function setColor($color) {
        $this->color = $color;
        return $this;
    }

    public function setTooltip($tooltip) {
        $this->tooltip = $tooltip;
        return $this;
    }

    public function setVisible($visible) {
        $this->visible = $visible ? '' : ' invisible';
    }

    public function setHTML($html) {
        $this->html = $html;
        return $this;
    }

    protected function renderContent() {
        return $this->html;
    }

    public function __toString() {
        $style = 'color: '.$this->color.'; border-color: '.$this->color.';';
        return
            '<div class="tag '.$this->visible.'" style="'.$style.'"'
                        .' title="'.$this->tooltip.'">'
                .$this->renderContent()
            .'</div>';
    }
}
