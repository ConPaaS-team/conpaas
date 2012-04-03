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

require_module('logging');
require_module('db');

class TaskFarmManager extends OpenNebulaManager {

	const CONF_FILENAME = 'bagoftasks-opennebula.ini';

	protected $user_data_file;

	public function __construct($data) {
		parent::__construct($data);
	}

	protected function loadConfiguration() {
		parent::loadConfiguration();
		// override the service-specific parameters
		$conf = parse_ini_file(Conf::CONF_DIR.'/'.self::CONF_FILENAME, true);
		if ($conf === false) {
			throw new Exception('Could not read OpenNebula configuration file '
				.'opennebula.ini');
		}
		$this->instance_type = $conf['instance_type'];
		$this->user = $conf['user'];
		$this->passwd = $conf['passwd'];
		$this->image = $conf['image'];
		$this->user_data_file = $conf['user_data_file'];
	}

	public function createContextFile($cloud) {
		return file_get_contents($this->user_data_file);
	}
}
?>