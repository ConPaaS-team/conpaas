<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/page');

class ScalarisPage extends ServicePage {

	public function __construct(Service $service) {
		parent::__construct($service);
		$this->addJS('js/scalaris.js');
	}

  
	protected function renderMngmtConsole() {
		if (!$this->service->isRunning()) {
			return '';
		}
		return LinkUI('management console',
			      'http://'.$this->service->getMngmtServAddr().':8000')
			              ->setExternal(true).'&middot';
	}


	protected function renderRightMenu() {
		return '<div class="rightmenu">'
			.$this->renderMngmtConsole()
			.LinkUI('manager log',
				'viewlog.php?sid='.$this->service->getSID())
				       ->setExternal(true)
			.'</div>';
	}

	protected function renderInstanceActions() {
		return EditableTag()
			->setColor('blue')
			->setID('scalaris')
			->setValue('0')
			->setText('Scalaris DataNode');
	}

	public function renderContent() {
		return $this->renderInstancesSection();
	}
}

?>
