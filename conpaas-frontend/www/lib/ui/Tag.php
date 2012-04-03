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

function Tag () {
	return new Tag();
}

class Tag {

	protected $color = 'blue';
	private $html = '';

	/**
	 * posible colors are "blue", "purple" & "orange"
	 * If you want to add more colors, edit main CSS file
	 * @param string $color
	 */
	public function setColor($color) {
		$this->color = $color;
		return $this;
	}

	public function setHTML($html) {
		$this->html = $html;
		return $this;
	}

	protected function renderContent() {
		return $this->html;
	}

	public function __toString() {
		return
			'<div class="tag '.$this->color.'">'
				.$this->renderContent()
			.'</div>';
	}
}