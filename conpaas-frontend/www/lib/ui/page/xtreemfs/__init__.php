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

	private function renderUserInput() {
		return
			'<div id="certForm">'
				.'<div class="left-stack name">user</div>'
				.'<div class="left-stack details">'
					.'<input id="user" type="text" name="user" value="" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderGroupInput() {
		return
			'<div id="certForm">'
				.'<div class="left-stack name">group</div>'
				.'<div class="left-stack details">'
					.'<input id="group" type="text" name="group" value="" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderPassphraseInput() {
		return
			'<div id="certForm">'
				.'<div class="left-stack name">passphrase</div>'
				.'<div class="left-stack details">'
					.'<input type="password" name="passphrase" value="" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderAdminflagInput() {
		return
			'<div id="certForm">'
				.'<div class="left-stack name">admin flag</div>'
				.'<div class="left-stack details">'
					.'<input type="checkbox" name="adminflag" value="yes" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderFilenameInput($filename) {
		return
			'<div id="certForm">'
				.'<div class="left-stack name">filename</div>'
				.'<div class="left-stack details">'
					.'<input type="text" name="filename" value="'
						.$filename
					.'" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderUserCertificateForm() {
		return
		'<form id="userCertForm" action="/ajax/downloadSslCertificate.php" '
				.'method="get">'
			.'<input type="hidden" name="sid" value="'
				.$this->service->getSID()
			.'" />'
			.'<input type="hidden" name="cert_type" value="user" />'
			.$this->renderUserInput()
			.$this->renderGroupInput()
			.$this->renderPassphraseInput()
			.$this->renderAdminflagInput()
			.$this->renderFilenameInput('user_cert.p12')
			.'<div id="createCertForm" class="">'
				.'<div class="left-stack name"></div>'
				.'<div class="left-stack details">'
					.'<input id="downloadUserCert" type="button" '
						.'value="download" />'
					.'<i id="userCertStat" class="invisible"></i>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
		.'</form>';
	}

	private function renderClientCertificateForm() {
		return
		'<form id="clientCertForm" action="/ajax/downloadSslCertificate.php" '
				.'method="get">'
			.'<input type="hidden" name="sid" value="'
				.$this->service->getSID()
			.'" />'
			.'<input type="hidden" name="cert_type" value="client" />'
			.$this->renderPassphraseInput()
			.$this->renderAdminflagInput()
			.$this->renderFilenameInput('client_cert.p12')
			.'<div id="createCertForm" class="">'
				.'<div class="left-stack name"></div>'
				.'<div class="left-stack details">'
					.'<input id="downloadClientCert" type="button" '
						.'value="download" />'
					.'<i id="clientCertStat" class="invisible"></i>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
		.'</form>';
	}

	public function renderUserCertificateSection() {
		return
		'<div class="form-section xtreemfs-volume">'
			.'<div class="form-header">'
				.'<div class="title">Create User Certificate'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.$this->renderUserCertificateForm()
		.'</div>';
	}

	public function renderClientCertificateSection() {
		return
		'<div class="form-section xtreemfs-volume">'
			.'<div class="form-header">'
				.'<div class="title">Create Client Certificate'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.$this->renderClientCertificateForm()
		.'</div>';
	}

	public function renderContent() {
		$html = $this->renderInstancesSection();
		if($this->service->isRunning()){
			$html .= $this->renderVolumeForm(); 
		}
		$html .= $this->renderClientCertificateSection();
		$html .= $this->renderUserCertificateSection();

		return $html;
	}
}

?>
