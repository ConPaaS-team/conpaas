<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/page');

class HadoopPage extends ServicePage {

	public function __construct(Service $service) {
		parent::__construct($service);
		$this->addJS('js/hadoop.js');
	}

	protected function renderRightMenu() {
		$links = LinkUI('manager log',
			'viewlog.php?sid='.$this->service->getSID())
			->setExternal(true);
		if ($this->service->isRunning()) {
			$master_addr = $this->service->getAccessLocation();
			$links .= ' &middot; '
				.LinkUI('namenode', $master_addr.':50070')
					->setExternal(true)
				.' &middot; '
				.LinkUI('job tracker', $master_addr.':50030')
					->setExternal(true)
				.' &middot; '
				.LinkUI('HUE', $master_addr.':8088')
					->setExternal(true);
		}
		return '<div class="rightmenu">'.$links.'</div>';
	}

	protected function renderInstanceActions() {
		return EditableTag()
			->setColor('purple')
			->setID('workers')
			->setValue('0')
			->setText('Hadoop DataNode & TaskTracker');
	}

	public function renderContent() {
		return $this->renderInstancesSection();
	}
}

?>
