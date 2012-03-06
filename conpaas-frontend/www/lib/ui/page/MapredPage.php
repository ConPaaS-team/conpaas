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

class MapredPage {

	static $states = array(
		'INIT' => false,
		'RUNNING' => false,
		'PROLOGUE' => true,
		'EPILOGUE' => true,
		'STOPPED' => false
	);

	private $managerAddress;
	private $conf = null;

	public function __construct($data) {
		$this->managerAddress = $data['manager'];
	}

	public function is_transient($state) {
		return
			!array_key_exists($state, self::$states) ||
			(self::$states[$state] == true);
	}

	public function getUploadURL() {
		return $this->managerAddress;
	}

	public function fetchState() {
		return 'RUNNING';
	}

	public function renderActions($state) {
		$startButton = InputButton('start')
			->setId('start');
		$stopButton = InputButton('stop')
			->setId('stop');
		$terminateButton = InputButton('terminate')
			->setDisabled(true);

		switch ($state) {
			case 'INIT':
				$stopButton->setVisible(false);
				$terminateButton->setVisible(false);
				break;
			case 'RUNNING':
				$startButton->setVisible(false);
				$terminateButton->setVisible(false);
				break;
			case 'STOPPED':
				$stopButton->setVisible(false);
				break;
			default:
		}

		return $startButton.' '.$stopButton.' '.$terminateButton;
	}

	public function renderStateClass($state) {
		switch ($state) {
			case 'INIT':
			case 'RUNNING':
				return 'active';
			case 'STOPPED':
				return 'stopped';
			default:
				return '';
		}
	}

}

?>