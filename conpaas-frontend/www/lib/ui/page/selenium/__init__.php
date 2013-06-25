<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/page');

class SeleniumPage extends ServicePage {
    public function __construct(Service $service) {
            parent::__construct($service);
            $this->addJS('js/selenium.js');
    }

    protected function renderRightMenu() {
        $links = LinkUI('manager log',
            'viewlog.php?sid='.$this->service->getSID())->setExternal(true);

        if ($this->service->isRunning()) {
            $console_url = $this->service->getAccessLocation();
            $links .= ' &middot; ' .LinkUI('hub', $console_url)->setExternal(true);
        }

        return '<div class="rightmenu">'.$links.'</div>';
    }

    protected function renderInstanceActions() {
        return EditableTag()->setColor('purple')->setID('node')->setValue('0')->setText('Selenium Nodes');
    }

    public function renderContent() {
        return $this->renderInstancesSection();
    }
}
?>
