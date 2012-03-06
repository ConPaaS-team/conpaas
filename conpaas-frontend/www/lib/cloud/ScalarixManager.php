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
require_module('http');
require_module('service');

class ScalarixManager extends OpenNebulaManager {

	const ROOT_URL = 'http://localhost:4567/jsonrpc';

	private $url;

	public function __construct($service_data) {
		parent::__construct($service_data);
		$this->url = $service_data['manager'];
	}

	/**
	 * Instantiate a virtual image of the Manager.
	 *
	 * @return string id of the virtual instance
	 * @throws Exception
	 */
	public function run() {
		$json = HTTP::jsonrpc(self::ROOT_URL, 'post', 'create_scalaris',
			array('New Scalarix'));
		$response = json_decode($json, true);
		if ($response == null) {
			dlog('run(): Error decoding JSON: '.$response);
		}
		$this->url = $response['result'];
		// update the manager
		ServiceData::updateManagerAddress($this->sid, $this->url,
			Service::STATE_INIT);
	}

	/**
	 * @return false if the state is not 'running'
	 * 		   the address (DNS) of the instance
	 * @throws Exception
	 */
	public function getAddress() {
		return false;
	}

	public function terminate() {
		$json = HTTP::jsonrpc(self::ROOT_URL, 'post', 'destroy_scalaris',
			array($this->url));
	}
}
