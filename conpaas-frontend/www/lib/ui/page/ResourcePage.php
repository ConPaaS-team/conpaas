<?php

require_module('logging');
require_module('ui');

class ResourcePage extends Page {
	

	public function __construct() {
		parent::__construct();
		$this->addJS('js/resources.js');
	}

	protected function renderBackLinks() {
		$dashboard = LinkUI('Dashboard', 'index.php')
			->setIconPosition(LinkUI::POS_LEFT)
			->setIconURL('images/link_s_back.png');
		
		return $dashboard;
	}

	public function renderPageStatus() {
		return
			'<div id="pgstat">'
			.'<div id="backLinks">'
				.$this->renderBackLinks()
			.'</div>'
			.'<div id="pgstatRightWrap" style="display:none">'
			.'<div id="pgstatLoading" class="invisible">'
				.'<span id="pgstatLoadingText">creating service...</span>'
				.'<img class="loading" src="images/icon_loading.gif" style="vertical-align: middle;" /> '
			.'</div>'
			.'<div id="pgstatTimer" class="invisible">'
				.'<img src="images/refresh.png" /> recheck in '
				.'<i id="pgstatTimerSeconds">6</i> seconds '
			.'</div>'
				.'<div id="pgstatInfo" class="invisible">'
					.'<img src="images/info.png" style="margin-right: 5px;"/>'
					.'<span id="pgstatInfoText">service is starting</span>'
				.'</div>'
				.'<div id="pgstatError" class="invisible">'
					.'<img src="images/error.png" style="vertical-align: middle; margin-right: 5px;"/>'
					.'<span id="pgstatErrorName">service error</span>'
					.'<a id="pgstatErrorDetails" href="javascript: void(0);">'
						.'<img src="images/link_s.png" />details'
					.'</a>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.'<div class="clear"></div>'
			.'</div>';
	}

}
