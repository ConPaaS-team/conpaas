<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui/page');

class XtreemFSPage extends ServicePage {

	public function __construct(Service $service) {
		parent::__construct($service);
		// it's kind of a hack, but there are identical for now
		$this->addJS('js/xtreemfs.js');
	}

	protected function renderRightMenu() {
		$links = LinkUI('manager log',
			'viewlog.php?sid='.$this->service->getSID())
			->setExternal(true);
		if ($this->service->isRunning()) {
			$links .= ' &middot; '
				.LinkUI('volumes', 'viewVolumes.php?sid='.$this->service->getSID())
					->setExternal(true);
		}
		return '<div class="rightmenu">'.$links.'</div>';
	}
	protected function renderInstanceActions() {
		return EditableTag()
			->setColor('orange')
			->setID('osd')
			->setValue('0')
			->setText('XtreemFS OSD');
	}

	private function renderVolumeInput(){
		return
			'<div id="volumeForm">'
			.'<div class="left-stack name">volume name</div>'
			.'<div class="left-stack details">'
					.'<input id="volume" type="text" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}
	private function renderOwnerInput(){
		return
			'<div id="volumeForm">'
			.'<div class="left-stack name">owner</div>'
			.'<div class="left-stack details">'
					.'<input id="owner" type="text" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}
	private function renderVolumeCreate(){
		return $this->renderVolumeInput()
           .$this->renderOwnerInput()     
           .'<div id="createVolumeForm" class="">'
				.'<div class="left-stack name"></div>'
				.'<div class="left-stack details">'
					.'<input id="createVolume" type="button" '
					.' value="create volume" />'
					.'<input id="deleteVolume" type="button" '
					.' value="delete volume" />'
                    .'<i id="VolumeStat" class="invisible"></i>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	public function renderVolumeForm(){
		return
		'<div class="form-section xtreemfs-volume">'
			.'<div class="form-header">'
				.'<div class="title">XtreemFS Volume'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.$this->renderVolumeCreate()
		.'</div>';
	}
	public function renderContent() {
		$html = $this->renderInstancesSection();
		if($this->service->isRunning()){
			$html .= $this->renderVolumeForm(); 
		}
	
		return $html;
	}
}

?>
