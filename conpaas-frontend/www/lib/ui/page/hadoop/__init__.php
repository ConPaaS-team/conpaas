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
		// it's kind of a hack, but there are identical for now
		$this->addJS('js/scalaris.js');
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