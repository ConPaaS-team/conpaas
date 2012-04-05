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
require_module('db');
require_module('aws-sdk');

class EC2Manager extends Manager {

	private $ec2;

	private $manager_ami;
	private $security_group;
	private $keypair;
	private $user_data_file;

	public function __construct($data) {
		parent::__construct($data);
		$this->ec2 = new AmazonEC2();
		$this->loadConfiguration();
	}

	private function loadConfiguration() {
		$conf = parse_ini_file(Conf::CONF_DIR.'/aws.ini', true);
		if ($conf === false) {
			throw new Exception('Could not read AWS configuration file aws.ini');
		}
		$this->manager_ami = $conf['ami'];
		$this->security_group = $conf['security_group'];
		$this->keypair = $conf['keypair'];
		$this->user_data_file = $conf['user_data_file'];
		$this->instance_type = $conf['instance_type'];
	}

	/**
	 * Instantiate a virtual image of the Manager.
	 *
	 * @return string id of the virtual instance
	 * @throws Exception
	 */
	public function run() {
		$user_data = $this->createContextFile('ec2');
		$response = $this->ec2->run_instances($this->manager_ami, 1, 1, array(
			'InstanceType' => $this->instance_type,
			'KeyName' => $this->keypair,
			'SecurityGroup' => $this->security_group,
			'UserData' => base64_encode($user_data),
		));
		if (!$response->isOK()) {
			dlog($response);
			throw new Exception('the EC2 instance was not created');
		}
		/* get the instance id */
		$instance = $response->body->instancesSet->item;
		return $instance->instanceId;
	}

	public function resolveAddress($vmid) {
		$response = $this->ec2->describe_instances(array(
			'InstanceId' => $vmid,
		));
		if (!$response->isOK()) {
			dlog($response);
			throw new Exception('describe_instances call failed');
		}
		$instance = $response->body->reservationSet->item->instancesSet->item;
		if (!$instance->instanceState->name == 'running') {
			return false;
		}
		if (!isset($instance->dnsName) || $instance->dnsName == '') {
			return false;
		}
		return $instance->dnsName;
	}

	/**
	 * @param $vmid id of the virtual instance we are fetching address for
	 * @return the address (DNS) of the instance
	 * 		   false if the state is not 'running'
	 * @throws Exception
	 */
	public function getAddress() {
		return $this->resolveAddress($this->vmid);
	}

	public function terminate() {
		$response = $this->ec2->terminate_instances($this->vmid);
		if (!$response->isOK()) {
			dlog($response);
			throw new Exception('terminate_instances('.$this->vmid.') '.
				'failed for service '.$this->name.'['.$this->sid.']');
		}
	}

}
?>
