<?php 

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