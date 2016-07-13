<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/page');
require_module('ui/instance');
require_module('application');

class Dashboard extends Page {

    public function __construct() {
        parent::__construct();
        $this->addJS('js/service.js');
        $this->addJS('js/application.js');
    }

    public function renderAppManagerSection() {
        return
            '<div class="form-section">'
		.'<div id="instancesWrapper" style="display:none">'
		    .'<div class="brief">1 instance running</div>'
		    .'<div id="instances">'
			.$this->renderAppManagerInstance()
		    .'</div>'
		.'</div>'
	    .'</div>';
    }

    public function renderServicesSection() {
        return
            '<div class="form-section">'
                .'<div id="servicesWrapper">'
                .'</div>'
            .'</div>';
    }

    private function getApplicationNameByID($aid) {
        $applications_data = ApplicationData::getApplications($_SESSION['uid'], $aid);
        if (count($applications_data) > 0)
            $application = new Application($applications_data[0]);
            return $application->getName();
        return '';
    }

    protected function renderAppManagerInstance() {
        $cluster = new Cluster(array('manager'));
        // actual values for the ID and IP address will be filled in
        // by the javascript in application.js
        $cluster->addNode(new ManagerInstance('', ''));
        return $cluster->render();
    }

    // private function getApplicationNameByID($aid) {
    //     $applications_data = ApplicationData::getApplications($_SESSION['uid']);
    //     foreach ($applications_data as $application_data) {
    //         $application = new Application($application_data);
    //         if ($application->getAID() == $aid) {
    //             return $application->getName();
    //         }

    //     }
    //     return '';
    // }

    protected function renderRightMenu() {
        return
            '<div id="appRightMenu" class="rightmenu" style="display:none">'.
                LinkUI('application manager log',
                    'viewlog.php?aid='.$_SESSION['aid'])
                    ->setExternal(true).
            '</div>';
    }

    private function renderName() {
        return
            '<div class="nameWrapper">'
                .'<i id="name" class="name editable" title="click to edit">'
                    .$this->getApplicationNameByID($_SESSION['aid'])
                .'</i>'
            .'</div>';
    }

    private function renderAppControlButtons() {
        return
	    '<div class="menu">'
		.'<br><br><br>'
		.'<table style="width:100%"><tr><td>'
		.'<a id="btnAddService" class="button" href="addservice.php" style="display:none">'
		    .'<img  src="images/service-plus.png"/> add new service'
		.'</a>'
		.'<a id="btnStartApp" class="button" href="#" style="display:none">'
		    .'<img  src="images/play.png"/> start application'
		.'</a>'
		.'<br><br>'
		.$this->renderCloudProviders('default', false)
		.'</td><td align="right">'
		    .'<a id="btnStopApp" class="button" href="#" style="display:none">'
			.'<img src="images/remove.png"/> stop application'
		    .'</a>'
		.'</td></tr></table>'
	    .'</div>';
    }

    public function renderTopMenu() {
        return
        '<div class="pageheader">'
	    .'<div class="info">'
		.$this->renderName()
	    .'</div>'
	    .$this->renderRightMenu()
	    .$this->renderAppControlButtons()
	    .'<div class="clear"></div>'
      .'</div>';
    }

    protected function renderBackLinks() {
        $app = LinkUI('Dashboard', 'index.php')
            ->setIconPosition(LinkUI::POS_LEFT)
            ->setIconURL('images/link_s_back.png');

        return $app;
    }

    public function renderContent() {
        return
            $this->renderAppManagerSection()
            .$this->renderServicesSection();
    }
}
