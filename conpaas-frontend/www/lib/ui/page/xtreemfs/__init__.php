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

	private function renderVolumeInput() {
		return
			'<div>'
			.'<div class="left-stack name">volume name</div>'
			.'<div class="left-stack details">'
					.'<input id="volume" type="text" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderOwnerInput() {
		return
			'<div>'
			.'<div class="left-stack name">owner</div>'
			.'<div class="left-stack details">'
					.'<input id="owner" type="text" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	public function renderVolumeList($volumes) {
		if (count($volumes) == 0) {
			return '<div id="noVolumesBox" class="box xtreemfs-box">'
						.'You have no volumes in this XtreemFS service. '
						.'Go ahead and '
						.'<a class="linkVolumes" href="javascript:void(0);">'
						.'create a volume'
						.'</a>.'
					.'</div>';
		}
		$html = '<table class="slist volumes" cellpadding="0" cellspacing="1">';
		for ($i = 0; $i < count($volumes); $i++) {
			$volumeUI = XtreemFSVolume($volumes[$i]);
			if ($i == count($volumes) - 1) {
				$volumeUI->setLast();
			}
			$html .= $volumeUI;
		}
		$html .= '</table>';
		return $html;
	}

	private function renderAvailableVolumes($volumes) {
		return
			'<div id="availableVolumesForm">'
				.'<div class="left-stack name">available volumes</div>'
				.'<div class="left-stack details">'
					.'<div id="volumeListWrapper" class="xtreemfs-list">'
						.$this->renderVolumeList($volumes)
					.'</div>'
				.'</div>'
				.'<div class="clear"></div>'
				.'<div class="left-stack name"></div>'
				.'<div class="left-stack details">'
					.'<input id="refreshVolumeList" '
						.'type="button" value="refresh volumes" />'
					.'<i id="listVolumeStat" class="invisible"></i>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderVolumeCreate() {
		return $this->renderVolumeInput()
           .$this->renderOwnerInput()     
           .'<div id="createVolumeForm">'
				.'<div class="left-stack name"></div>'
				.'<div class="left-stack details">'
					.'<input id="createVolume" type="button" '
					.' value="create volume" />'
                    .'<i id="VolumeStat" class="invisible"></i>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	public function renderManageVolumesSection($volumes) {
		return
		'<div class="form-section xtreemfs-volume xtreemfs-available">'
			.'<div class="form-header">'
				.'<div class="title">'
					.'<img src="images/volume.png" />Manage XtreemFS Volumes'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.$this->renderAvailableVolumes($volumes)
		.'</div>'
		.'<div class="form-section xtreemfs-volume xtreemfs-create">'
			.$this->renderVolumeCreate()
		.'</div>';
	}

	private function renderUserInput() {
		return
			'<div>'
				.'<div class="left-stack name">user</div>'
				.'<div class="left-stack details">'
					.'<input id="user" type="text" name="user" value="" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderGroupInput() {
		return
			'<div>'
				.'<div class="left-stack name">group</div>'
				.'<div class="left-stack details">'
					.'<input id="group" type="text" name="group" value="" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderPassphraseInput() {
		return
			'<div>'
				.'<div class="left-stack name">passphrase</div>'
				.'<div class="left-stack details">'
					.'<input type="password" name="passphrase" '
							.'value="" autocomplete="off" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderRetypePassphraseInput() {
		return
			'<div>'
				.'<div class="left-stack name">retype passphrase</div>'
				.'<div class="left-stack details">'
					.'<input type="password" name="passphrase2" '
							.'value="" autocomplete="off" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderAdminflagInput() {
		return
			'<div>'
				.'<div class="left-stack name">admin flag</div>'
				.'<div class="left-stack details">'
					.'<input type="checkbox" name="adminflag" value="yes" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderFilenameInput($filename) {
		return
			'<div>'
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
			.$this->renderRetypePassphraseInput()
			.$this->renderAdminflagInput()
			.$this->renderFilenameInput('user_cert.p12')
			.'<div id="createCertForm" class="">'
				.'<div class="left-stack name"></div>'
				.'<div class="left-stack details">'
					.'<input id="downloadUserCert" type="button" '
						.'value="download certificate" />'
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
			.$this->renderRetypePassphraseInput()
//			.$this->renderAdminflagInput()
			.$this->renderFilenameInput('certificate.p12')
			.'<div id="createCertForm" class="">'
				.'<div class="left-stack name"></div>'
				.'<div class="left-stack details">'
					.'<input id="downloadClientCert" type="button" '
						.'value="download certificate" />'
					.'<i id="clientCertStat" class="invisible"></i>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
		.'</form>';
	}

	public function renderUserCertificateSection() {
		return
		'<div id="Create_User_Certificate" class="form-section xtreemfs-volume">'
			.'<div class="form-header">'
				.'<div class="title">'
					.'<img src="images/certificate.png" />Create User Certificate'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.$this->renderUserCertificateForm()
		.'</div>';
	}

	public function renderClientCertificateSection() {
		return
		'<div id="Create_Client_Certificate" class="form-section xtreemfs-volume">'
			.'<div class="form-header">'
				.'<div class="title">'
					.'<img src="images/certificate.png" />Access credentials'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.$this->renderClientCertificateForm()
		.'</div>';
	}

	private function renderServerAddress() {
		return
			'<div>'
				.'<div class="left-stack name">DIR address</div>'
				.'<div id="dirAddress" class="left-stack details">'
					.$this->service->getAccessLocation()
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	public function renderVolumeSelectorOptions($volumes) {
		$selectorContent = '';
		$hint = '';
		if (count($volumes) == 0) {
			$hint = '<b id="hintVolume" class="xtreemfs-hint">'
						.'To access the service you must first '
						.'<a class="linkVolumes" href="javascript:void(0);">'
							.'create a volume'
						.'</a>'
					.'</b>';
		} else {
			for ($i = 0; $i < count($volumes); $i++) {
				$selectorContent .=
					'<option value="'.$volumes[$i]['volumeName'].'">'
						.$volumes[$i]['volumeName']
					.'</option>';
			}
		}
		return
			'<select id="selectVolume" class="xtreemfs-select">'
			.$selectorContent
			.'</select>'
			.'<input id="refreshSelect" type="button" value="refresh" />'
			.$hint
			.'<i id="selectVolumeStat" class="invisible"></i>';
	}

	private function renderVolumeSelector($volumes) {	
		return
			'<div>'
				.'<div class="left-stack name">volume</div>'
				.'<div id="volumeSelectorWrapper" class="left-stack details">'
					.$this->renderVolumeSelectorOptions($volumes)
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderMountPointInput() {
		return
			'<div>'
				.'<div class="left-stack name">mount point</div>'
				.'<div class="left-stack details">'
					.'<input id="mountPoint" type="text" value="" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderCertFilenameInput() {
		return
			'<div>'
				.'<div class="left-stack name">certificate filename</div>'
				.'<div class="left-stack details">'
					.'<input id="certFilename" type="text" value="" />'
					.'<b id="hintCert" class="xtreemfs-hint">'
						.'To access the service you must first '
						.'<a id="linkCert" href="#Create_Client_Certificate">'
							.'create a certificate'
						.'</a>'
					.'</b>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderMountCommand() {
		$cmd = 'mount.xtreemfs '.$this->service->getAccessLocation()
				.'/<volume> <mount-point> '
				.'--pkcs12-file-path <client_cert.p12> '
				.'--pkcs12-passphrase <passphrase>';
		return
			'<div>'
				.'<div class="left-stack name">'
					.'<div class="xtreemfs-command">'
						.'<img src="images/terminal.png" title="shell command" />'
					.'</div><div class="xtreemfs-command">'
						.'mount<br/>command'
					.'</div>'
				.'</div>'
				.'<div class="left-stack details">'
					.'<input class="command" type="text" readonly="readonly" '
						.' id="mountCommand" value="'.$cmd.'" title="shell command"/>'
					.'<b class="xtreemfs-hint"> Click on the command to copy it</b>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderUnmountCommand() {
		$cmd = 'fusermount -u <mount-point>';
		return
			'<div>'
				.'<div class="left-stack name">'
					.'<div class="xtreemfs-command">'
						.'<img src="images/terminal.png" title="shell command" />'
					.'</div><div class="xtreemfs-command">'
						.'unmount<br/>command'
					.'</div>'
				.'</div>'
				.'<div class="left-stack details">'
					.'<input class="command" type="text" readonly="readonly" '
						.' id="unmountCommand" value="'.$cmd.'" title="shell command"/>'
					.'<b class="xtreemfs-hint"> Click on the command to copy it</b>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	public function renderAccessSection($volumes) {
		return
		'<div id="XtreemFS_Access" class="form-section xtreemfs-volume">'
			.'<div class="form-header">'
				.'<div class="title">'
					.'<img src="images/key.png" />XtreemFS Access'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.$this->renderServerAddress()
			.$this->renderVolumeSelector($volumes)
			.$this->renderMountPointInput()
			.$this->renderCertFilenameInput()
			.$this->renderMountCommand()
			.$this->renderUnmountCommand()
		.'</div>';
	}

	public function renderContent() {
		$html = $this->renderInstancesSection();
		$html .= $this->renderClientCertificateSection();
//		$html .= $this->renderUserCertificateSection();
		if($this->service->isRunning()){
			$volumes = $this->service->listVolumes();
			$html .= $this->renderManageVolumesSection($volumes);
			$html .= $this->renderAccessSection($volumes);
		}

		return $html;
	}
}

?>
