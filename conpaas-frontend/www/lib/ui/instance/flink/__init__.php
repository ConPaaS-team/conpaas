<?php

require_module('ui/instance');

class FlinkInstance extends Instance {

    public function __construct($info) {
        parent::__construct($info);
    }

    protected function renderCapabs() {
        $html = '';
        if ($this->info['is_master']) {
            $html .= '<div class="tag blue">master</div>';
        } else {
            $html .= '<div class="tag orange">worker</div>';
        }
        return $html;
    }

}

?>
