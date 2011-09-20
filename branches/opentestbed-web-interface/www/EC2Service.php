<?php

require_once('logging.php');
require_once('Service.php');
require_once('DB.php');
require_once('lib/aws-sdk/sdk.class.php');

class EC2 {
	
	protected $vmid;
	
	private $ec2;
	
	private $manager_ami;
	private $security_group;
	private $keypair;
	private $user_data_file;
	private $instance_type;
	private $service_type;
	
	public function __construct($data) {
		$this->service_type = $data['type'];
		$this->sid = $data['sid'];
		$this->vmid = $data['vmid'];
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
	 * @return string id of the virtual instance
	 * @throws Exception
	 */
	public function createManagerInstance() {
		$user_data = file_get_contents($this->user_data_file);
		if ($user_data === false) {
			throw new Exception('could not read manager user data: '.
				$this->user_data_file);
		}
		$user_data = str_replace(
						array('%CONPAAS_SERVICE_TYPE%', '%CONPAAS_SERVICE_ID%'),
						array(strtoupper($this->service_type), $this->sid),
						$user_data);
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
	
	/**
	 * @return false if the state is not 'running'
	 * 		   the address (DNS) of the instance
	 * @throws Exception
	 */
	public function getManagerAddress() {
		$response = $this->ec2->describe_instances(array(
			'InstanceId' => $this->vmid,
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
	
	public function terminateService() {
		$response = $this->ec2->terminate_instances($this->vmid);
		if (!$response->isOK()) {
			dlog($response);
			throw new Exception('terminate_instances('.$this->vmid.') '.
				'failed for service '.$this->name.'['.$this->sid.']');
		}
	}
	
}
?>
