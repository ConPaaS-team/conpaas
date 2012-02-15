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

class HTTP {

	private static $CURL_OPTS = array(
    	CURLOPT_CONNECTTIMEOUT => 5,
    	CURLOPT_RETURNTRANSFER => true,
    	CURLOPT_TIMEOUT        => 60,
	);

	public static function req($url, $http_method, array $data, $ping=false,
			$rpc=true) {
		$opts = self::$CURL_OPTS;
		if ($rpc) {
		  $opts[CURLOPT_HTTPHEADER] = array('Expect:',
		  	'Content-Type: application/json');
		} else {
		  $opts[CURLOPT_HTTPHEADER] = array('Expect:');
		}
		if ($ping) {
			$opts[CURLOPT_CONNECTTIMEOUT] = 1;
		}

		$http_method = strtolower($http_method);
		if ($http_method == 'post') {
			$opts[CURLOPT_POST] = 1;
			if ($rpc) {
  			  $opts[CURLOPT_POSTFIELDS] = json_encode($data);
			} else {
			  $opts[CURLOPT_POSTFIELDS] = $data;
			}
		}
		$opts[CURLOPT_URL] = $url;

		$conn = curl_init();
		curl_setopt_array($conn, $opts);
		$result = curl_exec($conn);
		if ($result === false) {
			$e = new Exception('Error sending cURL '.$http_method.' request to '
				.$url.' '.'Error code: '.curl_errno($conn).' '
				.'Error msg: '.curl_error($conn)
			);
			curl_close($conn);
			throw $e;
		}
		curl_close($conn);
		return $result;
	}

	public static function get($url, $ping=false) {
		return HTTP::req($url, 'get', array(), $ping, false);
	}

	public static function post($url, $data, $ping=false) {
		return HTTP::req($url, 'post', $data, $ping, false);
	}

	public static function jsonrpc($url, $http_method, $rpc_method, $params,
			$ping=false) {
		$data = array();
		if ($http_method == 'get') {
			// TODO(claudiugh): not sure if this is still part of the protocol
			$url .= '?'.http_build_query(array(
						'method' => $rpc_method,
						'params' => json_encode($params),
						'id' => 1),
					null, '&');
		} else {
			$data = array(
  				'method' => $rpc_method,
  				'params' => $params,
				'jsonrpc' => "2.0",
  				'id' => 1);
		}
		return HTTP::req($url, $http_method, $data, $ping, true);
	}

}
