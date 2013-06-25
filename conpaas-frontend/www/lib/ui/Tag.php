<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



function Tag () {
    return new Tag();
}

class Tag {

    protected $color = 'blue';
    protected $visible = '';
    private $html = '';

    /**
     * posible colors are "blue", "purple" & "orange"
     * If you want to add more colors, edit main CSS file
     * @param string $color
     */
    public function setColor($color) {
        $this->color = $color;
        return $this;
    }

    public function setVisible($bool) {
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
        return
            '<div class="tag '.$this->color.$this->visible.'">'
                .$this->renderContent()
            .'</div>';
    }
}
