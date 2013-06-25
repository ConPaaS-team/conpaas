<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('logging');
require_module('db');
//require_module('aws-sdk');

class EC2Manager extends Manager {

	private $ec2;

	private $manager_ami;
	private $security_group;
	private $keypair;

	public function __construct($data) {
		parent::__construct($data);
		$this->ec2 = new AmazonEC2();
		$this->loadConfiguration();
		$this->ec2->set_region($this->region);
	}

	private function loadConfiguration() {
		$conf = parse_ini_file(Conf::CONF_DIR.'/aws.ini', true);
		if ($conf === false) {
			throw new Exception('Could not read AWS configuration file aws.ini');
		}
		$this->manager_ami = $conf['ami'];
		$this->security_group = $conf['security_group'];
		$this->keypair = $conf['keypair'];
		$this->instance_type = $conf['instance_type'];
		$this->region = $conf['region'];
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
		if (!$instance) {
			return false;
		}
		$instance = $instance->to_array();
		if (!$instance['instanceState']['name'] == 'running') {
			return false;
		}
		if (!isset($instance['dnsName']) || !$instance['dnsName']) {
			return false;
		}
		return $instance['dnsName'];
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
