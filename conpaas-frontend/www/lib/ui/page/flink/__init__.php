<?php

require_module('ui/page');

class FlinkPage extends ServicePage {
    public function __construct(Service $service) {
            parent::__construct($service);
            $this->addJS('js/jquery.form.js');
            $this->addJS('js/jquery-ui.js');
            $this->addJS('js/flink.js');
    }

    protected function renderRightMenu() {
        $links = '';
        if ($this->service->isRunning()) {
            $links .= LinkUI('Apache Flink Dashboard',
						     $this->service->getAccessLocation())
                    ->setExternal(true);
            $links .= ' &middot; ';
        }
        $links .= LinkUI('manager log',
            'viewlog.php?aid='.$this->service->getAID()
                      .'&sid='.$this->service->getSID())->setExternal(true);

        return '<div class="rightmenu">'.$links.'</div>';
    }

    protected function renderInstanceActions() {
        $role = 'worker';
        return EditableTag()->setColor(Role::getColor('flink', $role))
                            ->setID($role)
                            ->setValue('0')
                            ->setText('workers')
                            ->setTooltip(Role::getInfo('flink', $role));
    }

    public function renderContent() {
        $html = '';
        $html .= $this->renderInstancesSection();
        return $html;
    }

}
?>
