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

class Dashboard extends Page {

	public function __construct() {
		parent::__construct();
		$this->addJS('js/servicepage.js');
		$this->addJS('js/index.js');
	}

	public function renderPageHeader() {
		return
			'<div class="menu">'
  				.'<a class="button" href="create.php">'
  					.'<img src="images/service-plus.png" /> create new service'
  				.'</a>'
  			.'</div>'
  			.'<div class="clear"></div>';
	}

	public function renderContent() {

	}
}
