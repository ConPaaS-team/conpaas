<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
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
