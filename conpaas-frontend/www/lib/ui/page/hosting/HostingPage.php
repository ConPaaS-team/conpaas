<?php
/*
 * Copyright (C) 2010-2012 Contrail consortium.
 *
 * This file is part of ConPaaS, an integrated runtime environment
 * for elastic cloud applications.
 *
 * ConPaaS is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * ConPaaS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.
 */

require_module('ui');
require_module('ui/page');

class HostingPage extends ServicePage {

	public function __construct(Service $service) {
		parent::__construct($service);
		$this->addJS('js/jquery.form.js');
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
					.'<input type="radio" name="method" disabled="disabled" />'
						.'checking out repository'
					.'</div>'
				.'</div>'
				.'<div class="deployactions">'
					.$this->renderFileForm()
					.'<div class="additional">'
					.'<img class="loading invisible" '
						.' src="images/icon_loading.gif" />'
					.'<i class="positive invisible">Submitted successfully</i>'
					.'</div>'
					.'<div class="clear"></div>'
					.'<div class="hint">'
						.'example: <b>.zip</b>, <b>.tar</b> of your source tree'
					.'</div>'
				.'</div>'
				// this one is invisible for now
				.'<div class="deployactions invisible">'
					.'<input type="text" size="40" />'
					.'<input type="button" value="checkout" />'
					.'<div class="hint">'
						.'example: <b>git checkout git@10.3.45.1:repos/</b>'
					.'</div>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function getVersionDownloadURL($versionID) {
		return $this->service->getManager()
			.'?action=downloadCodeVersion&codeVersionId='.$versionID;
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
			.'</div>';
	}

}