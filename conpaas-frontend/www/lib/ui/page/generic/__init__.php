<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui');
require_module('ui/page');

class GenericPage extends ServicePage {
	
	public function __construct(Service $service) {
		parent::__construct($service);
		// $this->addJS('js/jquery.form.js');
		$this->addJS('js/generic.js');
		// if ($this->service->isRunning() && $this->needsPasswordReset()) {
		// 	$this->addMessage($this->passwordResetMessage(),
		// 		MessageBox::WARNING);
		// }
	}
	
	protected function renderStateChange() {
	    return '';	
	}

	public function renderContent() {
		//$html = $this->renderInstancesSection();
		//if ($this->service->isRunning()) {
			//$html .= $this->renderAccessForm()
				//.$this->renderLoadSection();
		//}
		//return $html;
		
		return '<div align="center" id="divcontent" style="padding: 20px;"></div>';
	}

}

?>
