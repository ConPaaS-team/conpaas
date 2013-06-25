<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('logging');

class HTTPS {

	private static $CURL_OPTS = array(
    	CURLOPT_CONNECTTIMEOUT => 5,
    	CURLOPT_RETURNTRANSFER => true,
    	CURLOPT_TIMEOUT        => 60,
	);

	public static function req($url, $http_method, array $data, $ping=false,
		$rpc=true, $uid=null) {

        if ($uid == null) {
            /* Act as the frontend */
            $cert    =       Conf::CONF_DIR."/certs/cert.pem"; 
            $key     =       Conf::CONF_DIR."/certs/key.pem";
            $ca_cert =       Conf::CONF_DIR."/certs/ca_cert.pem";
        }
        else {
            /* Act as user */
            $cert    =       sys_get_temp_dir(). "/$uid/cert.pem"; 
            $key     =       sys_get_temp_dir(). "/$uid/key.pem"; 
            $ca_cert =       Conf::CONF_DIR."/certs/ca_cert.pem";
        }

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
		$opts[CURLOPT_SSL_VERIFYPEER] = TRUE;
		$opts[CURLOPT_CAINFO] = $ca_cert;
		$opts[CURLOPT_SSL_VERIFYHOST] = 0; 
		$opts[CURLOPT_FAILONERROR] = 1; 
		$opts[CURLOPT_SSLCERT] =  $cert; 
		$opts[CURLOPT_SSLKEYTYPE] = 'PEM'; 
		$opts[CURLOPT_SSLKEY] = $key; 

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

	public static function get($url, $ping=false, $uid=null) {
		return HTTPS::req($url, 'get', array(), $ping, false, $uid);
	}

	public static function post($url, $data, $ping=false, $uid=null) {
		return HTTPS::req($url, 'post', $data, $ping, false, $uid);
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
		return HTTPS::req($url, $http_method, $data, $ping, true);
	}

}
