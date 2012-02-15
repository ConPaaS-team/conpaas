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

class TimeHelper {

	public static function timeRelativeDescr($utc_ts) {
		$ts = strftime("%s", $utc_ts);
		$delta = time() - $ts;
		if ($delta < 0) {
			// this is in the future
			return 'a few moments';
		}
		$delta = ($delta > 0) ? $delta : - $delta;
		static $seconds = array(
			'year' => 31536000, // 365 * days
			'month' => 2592000, // 30 * days
			'week' => 604800, // 7 * days
			'day' => 86400, // 24 * 60 * 60
			'hour' => 3600, // 60 * 60
			'minute' => 60
		);
		static $units = array('year', 'month', 'week', 'day', 'hour', 'minute');
		foreach ($units as $unit) {
			$count = (int) ($delta / $seconds[$unit]);
			if ($count > 0) {
				$suffix = ($count > 1) ? 's' : '';
				return $count.' '.$unit.$suffix;
			}
		}
		return 'a few moments';
	}

}
