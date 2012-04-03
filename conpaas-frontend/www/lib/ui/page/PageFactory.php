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

class PageFactory {

	public static function create($service) {
		$type = $service->getType();

		switch ($type) {
			case 'php':
				require_module('ui/page/hosting');
				return new PhpPage($service);
			case 'java':
				require_module('ui/page/hosting');
				return new JavaPage($service);
			case 'mysql':
				require_module('ui/page/mysql');
				return new MysqlPage($service);
			case 'taskfarm':
				require_module('ui/page/taskfarm');
				return new TaskFarmPage($service);
			case 'scalaris':
				require_module('ui/page/scalaris');
				return new ScalarisPage($service);
			case 'hadoop':
				require_module('ui/page/hadoop');
				return new HadoopPage($service);
			default:
				throw new Exception('Unknown service type');
		}
	}
}