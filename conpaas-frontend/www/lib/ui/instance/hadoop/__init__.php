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

require_module('ui/instance');

class HadoopInstance extends Instance {

	public function __construct($info) {
		parent::__construct($info);
	}

	protected function renderCapabs() {
		$html = '';
		if (isset($this->info['workers'])) {
			$html .= '<div class="tag orange">worker</div>';
		}
		if (isset($this->info['masters'])) {
			$html .= '<div class="tag blue">master</div>';
		}
		return $html;
	}
}

?>