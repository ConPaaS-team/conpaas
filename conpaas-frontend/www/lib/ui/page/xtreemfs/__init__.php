<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

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
