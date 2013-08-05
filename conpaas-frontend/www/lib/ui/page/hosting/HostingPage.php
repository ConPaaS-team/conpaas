<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui');
require_module('ui/page');

class HostingPage extends ServicePage {

	public function __construct(Service $service) {
		parent::__construct($service);
		$this->addJS('js/jquery-1.5.js');
		$this->addJS('js/jquery.form.js');
		$this->addJS('js/jquery-ui.js');
		$this->addJS('js/autoscaling_slider.js');
		$this->addJS('js/hosting.js');
	}

	protected function renderApplicationAccess() {
		if (!$this->service->isRunning()) {
			return '';
		}
		return LinkUI('access application', $this->service->getAccessLocation())
				->setExternal(true).' &middot; ';
	}

	protected function renderInstanceActions() {
		$html = '';
		static $roles = array(
			'proxy' => 'orange',
			'web' => 'blue',
			'backend' => 'purple'
		);
		foreach ($roles as $role => $color) {
			$name = ($role == 'backend') ? $this->service->getType() : $role;
			$html .= EditableTag()
				->setColor($color)
				->setID($role)
				->setValue('0')
				->setText($name);
		}
		return $html;
	}

	protected function renderAppLink() {
		if (!$this->service->isRunning()) {
			return '';
		}
		return LinkUI('access application', $this->service->getAccessLocation())
			->setExternal(true);
	}

	private function renderFileForm() {
		$url = 'ajax/uploadCodeVersion.php?sid='.$this->service->getSID();
		return
		'<form id="fileForm" action="'.$url.'" enctype="multipart/form-data">'
			.'<input id="file" type="file" name="code" />'
			.'<input type="hidden" name="description" value="no description" />'
		.'</form>';
	}

	private function bytesOf ($size_str) {
		switch (substr ($size_str, -1))	{
			case 'M': case 'm': return (int)$size_str * 1048576;
			case 'K': case 'k': return (int)$size_str * 1024;
			case 'G': case 'g': return (int)$size_str * 1073741824;
			default: return $size_str;
		}
	}

	private function minSize($size1, $size2) {
		$size1_int = $this->bytesOf($size1);
		$size2_int = $this->bytesOf($size2);
		if ($size1_int < $size2_int) {
			return $size1;
		} else {
			return $size2;
		}
	}

	protected function renderCodeForm() {
		return
			'<div id="deployform">'
				.'<div class="deployoptions">'
					.'<i>you may update the stage by</i>'
					.'<div class="deployoption">'
						.'<input type="radio" name="method" checked/>'
						.'uploading archive'
					.'</div>'
					.'<i>or by</i>'
					.'<div class="deployoption">'
					.'<input type="radio" name="method" />'
						.'checking out repository'
					.'</div>'
				.'</div>'
				.'<div class="deployactions">'
					.$this->renderFileForm()
					.'<div class="additional">'
					.'<img class="loading invisible" '
						.' src="images/icon_loading.gif" />'
					.'<i class="positive invisible">Submitted successfully</i>'
					.'<i class="error invisible"></i>'
					.'</div>'
					.'<div class="clear"></div>'
					.'<div class="hint">'
						.'example: <b>.zip</b>, <b>.tar</b> of your source tree'
						.' (max '.$this->minSize(ini_get('upload_max_filesize'), ini_get('post_max_size')).')'
					.'</div>'
				.'</div>'
				// this one is invisible for now
				.'<div class="deployactions invisible">'
					.'<textarea id="pubkey" cols="50" rows="5" name="pubkey"></textarea><br />'
					.'<div class="additional">'
					.'<img class="loading invisible" '
					    .' src="images/icon_loading.gif" />'
                                        .'<i class="positive invisible">Submitted successfully</i>'
					.'<i class="error invisible"></i>'
					.'</div>'
					.'<div class="clear"></div>'
					.'<div class="hint">'
					.'Paste your public key (the contents of <b>$HOME/.ssh/id_rsa.pub)</b>'
					.'</div>'
					.'<button id="submitPubKey">Submit key</button>'
                    .'<div class="hint"><br />'
                    .'You will then be able to checkout your repository as follows:<br />'
                    .'<b>git clone git@'.$this->service->getManagerInstance()->getHostAddress().':code</b>'
                    .'</div>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function getVersionDownloadURL($versionID) {
		$url = 'ajax/downloadCodeVersion.php?sid='.$this->service->getSID();
		$url.= '&codeVersionId='.$versionID;
		return $url;
	}

	public function renderCodeVersions() {
		$versions = $this->service->fetchCodeVersions();
		if ($versions === false) {
			return '<h3> No versions available </h3>';
		}
		$active = null;
		for ($i = 0; $i < count($versions); $i++) {
			if (isset($versions[$i]['current'])) {
				$active = $i;
			}
		}
		if (count($versions) == 0) {
			return '<h3> No versions available </h3>';
		}
		$html = '<ul class="versions">';
		for ($i = 0; $i < count($versions); $i++) {
			$versions[$i]['downloadURL'] =
				$this->getVersionDownloadURL($versions[$i]['codeVersionId']);
			$versionUI = Version($versions[$i])
				->setLinkable($this->service->isRunning());
			if ($active == $i) {
			  if ($this->service->isRunning()) {
				$versionUI->setActive(true,
					$this->service->getAccessLocation());
			  } else {
			    $versionUI->setActive(true);
			  }
			}
			if ($i == count($versions) - 1) {
				$versionUI->setLast();
			}
			$html .= $versionUI;
		}
		$html .= '</ul>';
		return $html;
	}

	public function renderCodeSection() {
		return
			'<div class="form-section">'
				.'<div class="form-header">'
					.'<div class="title">Code management</div>'
					.'<div class="access-box">'.$this->renderAppLink().'</div>'
					.'<div class="clear"></div>'
				.'</div>'
				.$this->renderCodeForm()
				.'<div class="brief">available code versions</div>'
				.'<div id="versionsWrapper">'
					.$this->renderCodeVersions()
				.'</div>'
			.'</div>'.$this->renderStartupScriptSection();
	}

}
