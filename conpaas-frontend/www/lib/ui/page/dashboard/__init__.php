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
  				.'<a class="button" href="create.php">'
  					.'<img src="images/service-plus.png" /> create new service'
  				.'</a>'
  			.'</div>'
  			.'<div class="clear"></div>';
	}

	private function getApplicationNameByID($aid) {
		$applications_data = ApplicationData::getApplications($aid);
		foreach ($applications_data as $application_data) {
			$application = new Application($application_data);
			if ($application->getAID() == $aid) {
				return $application->getName();
			}

			return '';
		}
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
  		.'<div class="clear"></div>'
  	.'</div>';
	}

	protected function renderBackLinks() {
		$app = LinkUI('Applications', 'index.php')
			->setIconPosition(LinkUI::POS_LEFT)
			->setIconURL('images/link_s_back.png');

		return $app;
	}

	public function renderContent() {

	}
}
