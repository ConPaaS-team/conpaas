<?php
/*
 * Copyright (C) 2010-2011 Contrail consortium.
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

require_module('ui/page');

class HadoopPage extends ServicePage {

	public function __construct(Service $service) {
		parent::__construct($service);
	}

	protected function renderRightMenu() {
		$master_addr = $this->service->getAccessLocation();
		return
			'<div class="rightmenu">'
				.LinkUI('manager log',
						'viewlog.php?sid='.$this->service->getSID())
					->setExternal(true)
				.' &middot; '
				.LinkUI('namenode', $master_addr.':50070')
					->setExternal(true)
				.' &middot; '
				.LinkUI('job tracker', $master_addr.':50030')
					->setExternal(true)
			.'</div>';
	}


	protected function _renderRightMenu() {
		// TODO: add specific info from Hadoop UI
		$manager = $this->service->getManagerIP();
		return
			'<div class="subname">'.
				$this->renderStateChange().
			'</div>';
	}
}

?>