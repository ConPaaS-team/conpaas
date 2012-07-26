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
require_module('service');
require_module('service/factory');
require_module('ui/instance/php');

class PHPService extends Service {

	protected $conf = null;
	protected $cds = null;

	public function __construct($data, $cloud) {
		parent::__construct($data, $cloud);
		if ($this->isCdnEnabled()) {
			$cds_data = ServiceData::getCdsByAddress($this->conf->cdn);
			$this->cds = ServiceFactory::create($cds_data);
		}
	}

	public function hasDedicatedManager() {
		return true;
	}

	public function getConfiguration() {
		if (!$this->isReachable()) {
			return null;
		}
		if ($this->conf !== null) {
			return $this->conf;
		}
		$json = $this->managerRequest('get', 'get_configuration', array());
		$conf = json_decode($json);
		if ($conf == null) {
			return null;
		}
		$this->conf = $conf->result;
		return $this->conf;
	}

	public function getAppAddress() {
		$loadbalancer = $this->getNodeInfo($this->nodesLists['proxy'][0]);
		return $loadbalancer['ip'];
	}

	public function sendConfiguration($params) {
		return $this->managerRequest('post', 'update_php_configuration',
			$params);
	}

	public function createInstanceUI($node) {
		$info = $this->getNodeInfo($node);
		return new PHPInstance($info);
	}

	public function getInstanceRoles() {
		return array('proxy', 'web', 'backend');
	}

	public function requestShutdown() {
		// if we have cds enabled, we need to unsubscribe from it because once
		// the service is stopped the origin address will be lost
		if ($this->cds) {
			$this->cdnEnable(false, '');
			$this->cds->unsubscribe($this->getAppAddress());
		}
		// regular shutdown
		return parent::requestShutdown();
	}

	public function isCdnEnabled() {
		$conf = $this->getConfiguration();
		if ($conf && isset($conf->cdn) && $conf->cdn) {
			return true;
		}
		return false;
	}

	public function getCds() {
		return $this->cds;
	}

	public function cdnEnable($enable, $address) {
		return $this->managerRequest('post', 'cdn_enable',
			array('enable' => $enable, 'address' => $address));
	}

	public function getAvailableCds($uid) {
		$services_data = ServiceData::getAvailableCds($uid);
		$services = array();
		foreach ($services_data as $service_data) {
			$services []= ServiceFactory::create($service_data);
		}
		return $services;
	}
}

?>