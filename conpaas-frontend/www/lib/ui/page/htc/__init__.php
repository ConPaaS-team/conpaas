<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



/*
 *	 TODO:	as this file was created from a BLUEPRINT file,
 *	 	you may want to change ports, paths and/or methods (e.g. for hub)
 *		to meet your specific service/server needs
 */
require_module('ui/page');

class HTCPage extends ServicePage {
    public function __construct(Service $service) {
            parent::__construct($service);
            $this->addJS('js/htc.js');
    }

    protected function renderRightMenu() {
        $links = LinkUI('manager log',
            'viewlog.php?sid='.$this->service->getSID())->setExternal(true);

        if ($this->service->isRunning()) {
            $console_url = $this->service->getAccessLocation();
            $links .= ' &middot; ' .LinkUI('agent', $console_url)->setExternal(true);
        }

        return "\n".'<div class="rightmenu">'.$links.'</div>';
    }

    protected function renderInstanceActions() {
        return EditableTag()->setColor('purple')->setID('node')->setValue('0')->setText('HTC Agents');
    }

    public function renderContent() {
        return $this->renderInstancesSection();
    }

    protected function renderIncompleteGUI() {
        return "\n".'<div class="info">This GUI is under construction. In the mean time please use the CLI for features missing in this GUI.</div>';
    }

    protected function renderServiceSelection() {
        $_modes = array( "demo", "real" );
        $radios = '';
        foreach($_modes as $_mode){
            $radio = Radio($_mode);
            $radio->setTitle("available_modes");

            if ($_mode === 'demo') {
                #$radio->setDefault();
                $radios = "\n".$radio;
            } else {
                $radios = $radios.'<br>'."\n".$radio;
            }
        }
        $_modeChoice = Tag();
        $_modeChoice->setHTML($radios);

        $_types = array( "batch", "online", "workflow" );
        $radios = '';
        foreach($_types as $_type){
            $radio = Radio($_type);
            $radio->setTitle("available_types");

            if ($_type === 'batch') {
                #$radio->setDefault();
                $radios = "\n".$radio;
            } else {
                $radios = $radios.'<br>'."\n".$radio;
            }
        }
        $_typeChoice = Tag();
        $_typeChoice->setHTML($radios);



        return $_modeChoice . ' ' . $_typeChoice;
    }
}
?>
