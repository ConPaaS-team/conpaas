<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/page');
require_module('application');

class Dashboard extends Page {

	public function __construct() {
		parent::__construct();
		$this->addJS('js/servicepage.js');
		$this->addJS('js/services.js');
	}

	public function renderPageHeader() {
		return
			'<div class="menu">'
  				.'<table style="width:100%"><tr><td>'
  				.'<a id="btnAddService" class="button" href="create.php" style="display:none">'
  					.'<img  src="images/service-plus.png"/> add new service'
  				.'</a>'
  				.'<a id="btnStartApp" class="button" href="#" style="display:none">'
  					.'<img  src="images/play.png"/> start application'
  				.'</a></td><td align="right">'
  				.'<a id="btnStopApp" class="button" href="#" style="display:none">'
  					.'<img  src="images/remove.png"/> stop application'
  				.'</a>'
  				.'</td></tr></table>'
  			.'</div>'
  			.'<div class="clear"></div>'
  			.'<br>'
  			.'<div id="instances"></div>'
  			;
	}



	private function getApplicationNameByID($aid) {
		$applications_data = ApplicationData::getApplications($_SESSION['uid'], $aid);
		if (count($applications_data) > 0)
			$application = new Application($applications_data[0]);
			return $application->getName();
		return '';
	}

	// private function getApplicationNameByID($aid) {
	// 	$applications_data = ApplicationData::getApplications($_SESSION['uid']);
	// 	foreach ($applications_data as $application_data) {
	// 		$application = new Application($application_data);
	// 		if ($application->getAID() == $aid) {
	// 			return $application->getName();
	// 		}

	// 	}
	// 	return '';
	// }

	protected function renderRightMenu() {
		return
			'<div class="rightmenu">'.
				LinkUI('application manager log', 'viewlog.php')
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

	public function renderTopMenu() {
		return
    	'<div class="pageheader">'
    		.'<div class="info">'
    			.$this->renderName()
    		.'</div>'
		.$this->renderRightMenu()
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

	}
}
