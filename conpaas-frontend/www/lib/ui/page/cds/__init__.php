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

require_module('cloud');
require_module('logging');
require_module('ui');
require_module('ui/page');

class CDSPage extends ServicePage {

	public function __construct(Service $service) {
		parent::__construct($service);
		$this->addJS('https://www.google.com/jsapi');
		$this->addJS('js/cds.js');
	}

	/**
	 * @overrides ServicePage::renderRightMenu()
	 */
	protected function renderRightMenu() {
		$managerHost = $this->service->getManagerInstance()->getHostAddress();
		return
			'<div class="rightmenu">'
				.Address($managerHost)
					->setTitle('manager address')
					->setWidth(350)
			.'</div>';
	}

	/**
	 * @override ServicePage::renderActions()
	 */
	public function renderActions() {
		return InputButton('terminate')
			->setId('terminate');
	}

	public function renderSubscribers() {
		$subscribers = $this->service->getSubscribers();
		if (count(array_keys($subscribers)) == 0) {
			return
			'<div class="box infobox">No applications are subscribed</div>';
		}
		$apps_html = '';
		foreach ($subscribers as $app => $details) {
			$ts = 'subscribed '.TimeHelper::timeRelativeDescr($details['mtime'])
				.' ago';
			$apps_html .=
			'<div class="app">'
				.'<div class="appname">'.$app.'</div>'
				.'<div class="timestamp">'.$ts.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
		}
		return
		'<div class="brief">applications subscribed</div>'
		.'<div class="apps">'
			.$apps_html
		.'</div>';
	}

	public function renderSubscribersSection() {
		return
		'<div class="form-section">'
			.$this->renderSubscribers()
		.'</div>';
	}

	private function renderEdgeLocation($edge_location) {
		return
		'<div class="instance">'
			.Address($edge_location['address'])
				->setTitle('edge location address')
		.'</div>';
	}

	private function renderRegion($cloud, $region) {
		$led = $region->hasEdgeLocations() ?
			'ledgreen.png' : 'ledlightblue.png';
		$edge = '';
		foreach ($region->edge_locations as $edge_location) {
			$edge .= $this->renderEdgeLocation($edge_location);
		}
		return
		'<div class="regionWrapper">'
		.'<div class="region">'
			.'<img src="'.$region->getFlagURL().'" class="country" />'
			.'<div class="title">'
				.$cloud->getName().' in '.$region
				.' <img src="images/'.$led.'" width="12" style="margin-left: 3px;" />'
				.'<div class="edge">'.$edge.'</div>'
				.'<div class="menu">'.
					InputButton('+ edge location')->setDisabled(true)
				.'</div>'
			.'</div>'
			.$cloud->getLogo()
			.'<div class="clear"></div>'
		.'</div>'
		.'</div>';
	}

	private function renderRegions() {
		$clouds = $this->service->joinRegionsWithSnapshot();
		$active_regions = '';
		$other_regions = '';
		foreach ($clouds as $cloud) {
			foreach ($cloud->regions as $region) {
				$html = $this->renderRegion($cloud, $region);
				if ($region->hasEdgeLocations()) {
					$active_regions .= $html;
				} else {
					$other_regions .= $html;
				}
			}
		}
		return $active_regions.$other_regions.'<div class="region-end"></div>';
	}

	public function renderMapSection() {
		return
		'<div class="form-section">'
		.'<div class="brief">available regions</div>'
		.'<div id="map-container" style="height: 300px;">'
			.'<div class="loading">loading map...</div>'
		.'</div>'
		.'<div class="map">'
			.$this->renderRegions()
		.'</div>'
		.'</div>';
	}

	public function renderLogSection() {
		$logLines = $this->service->getLog();
		$html = '';
		foreach ($logLines as $logLine) {
			$html .= '<div class="line">'.$logLine.'</div>';
		}
		return
		'<div class="form-section">'
			.'<div class="form-header">'
				.'<div class="title">'
					.'<img src="images/log.png" width="24"/>'
					.'<i>Network Monitor Log</i>'
				.'</div>'
				.'<div class="access-box">'
					.'<select id="loglines">'
						.'<option value="10">10</option>'
						.'<option value="20" selected="selected">20</option>'
						.'<option value="40">40</option>'
					.'</select>'
					.' lines'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.'<div class="log">'
				.$html
			.'</div>'
		.'</div>';
	}

	public function renderContent() {
		return
			$this->renderMapSection()
			.$this->renderSubscribersSection()
			.$this->renderLogSection();
	}
}