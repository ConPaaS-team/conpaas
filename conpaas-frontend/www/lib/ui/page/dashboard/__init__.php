<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/page');
require_module('application');

class Dashboard extends Page {

	public function __construct() {
		parent::__construct();
		$this->addJS('js/servicepage.js');
		$this->addJS('js/services.js');

		$this->addJS('js/jqplot/jquery.jqplot.min.js');
		$this->addJS('js/jqplot/jqplot.canvasAxisLabelRenderer.min.js');
		$this->addJS('js/jqplot/jqplot.canvasTextRenderer.js');
		$this->addJS('js/jqplot/jqplot.highlighter.min.js');
		$this->addJS('js/jqplot/jqplot.cursor.min.js');
		
		$this->addJS('js/codepress/codepress.js');


	}

	public function renderPageHeader() {
		// return
		// 	'<div class="menu">'
  // 				.'<a class="button" href="create.php">'
  // 					.'<img src="images/service-plus.png" /> create new service'
  // 				.'</a>'
  // 			.'</div>'
  // 			.'<div class="clear"></div>';
	}

	public function renderHeaderCSS()
	{
		$cssheader = parent::renderHeaderCSS();
		$cssheader .= parent::renderCSSLink('css/jquery.jqplot.min.css');
		return $cssheader;
	}


	private function getApplicationNameByID($aid) {
		$applications_data = ApplicationData::getApplications($_SESSION['uid']);
		foreach ($applications_data as $application_data) {
			$application = new Application($application_data);
			if ($application->getAID() == $aid) {
				return $application->getName();
			}

		}
		return '';
	}

	private function renderName() {
		$name = 'New application';
		
		if ($_SESSION['aid'] != 0){
			$name = $this->getApplicationNameByID($_SESSION['aid']);
		}
		return
			'<div class="nameWrapper">'
				.'<i id="name" class="name editable" title="click to edit">'
					. $name 
				.'</i>'
			.'</div>';
	}

	public function renderTopMenu() {
		return
    	'<div class="pageheader">'
    		.'<div class="info" style="display:inline">'
    			.$this->renderName()
    		.'</div>'
    		.'<a class="button" style="float:right; display:none" href="#"><img src="images/service-plus.png" /> add services</a>'
    		.'<a id="btnStartApp" class="button" style="float:right" href="#"><img src="images/service-plus.png" /> start</a>'
  		.'<div class="clear"></div>'
  	.'</div>';
	}
// '<a class="button" href="#"><img src="images/service-plus.png" /> add services</a>'
	protected function renderBackLinks() {
		$app = LinkUI('Applications', 'index.php')
			->setIconPosition(LinkUI::POS_LEFT)
			->setIconURL('images/link_s_back.png');

		return $app;
	}

	public function renderContent() {
        // $cont = '<form id="fileForm" enctype="multipart/form-data" style="width:100%">
        //     <table cellpadding="3" style="width:100%">          
        //     <tr><td style="width:150px">Application manifest: </td><td><input id="manfile" name="manfile" type="file"></td></tr>  
        //     <tr><td>Application: </td><td><input id="appfile" name="appfile" type="file"></td></tr>
        //     <tr><td>SLO:</td><td><textarea id="slotext" name="slo" style="width:100%; height:280px;"></textarea></td></tr>
        //     </table>
        //     </form>';
        $cont = '<div><table border="1" cellpadding="3" style="width:100%">          
             <tr><td style="width:150px">Application manifest: </td><td><form id="manform" action="ajax/parseManifest.php" method="POST"><input id="manfile" name="manfile" type="file"></form></td></tr>  
             <tr><td>Application: </td><td><input id="appfile" name="appfile" type="file"></td></tr>
             <!--tr><td>SLO:</td><td><textarea id="slotext" name="slo" style="width:100%; height:280px;"></textarea></td></tr-->
             </table></div>';


        return $cont;
	}
}
