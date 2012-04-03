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
		$response = $this->ec2->terminate_instances();
		if (!$response->isOK()) {
			dlog($response);
			throw new Exception('terminate_instances('.$this->vmid.') '.
				'failed for service '.$this->name.'['.$this->sid.']');
		}
	}

}
?>
