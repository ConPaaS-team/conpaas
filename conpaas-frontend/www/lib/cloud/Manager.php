<?php
// /* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ca');
require_module('logging');

class Manager {

	// protected $sid;
	protected $aid;
	protected $uid;
	protected $vmid;
	private $instance_type;
	// private $service_type;

	public function __construct($data) {
		// $this->service_type = $data['type'];
		// $this->sid = $data['sid'];
		$this->aid = $data['aid'];
		$this->uid = $data['uid'];
		$this->vmid = $data['vmid'];
		$this->ipaddr = $data['manager'];
	}

	public function getID() {
		return $this->vmid;
	}

	public function getHostAddress() {
		return $this->resolveAddress($this->vmid);
	}

	public function resolveAddress($vmid) {
        return $this->ipaddr;
	}
 
	public function terminate() {
        $res = HTTPS::post(Conf::DIRECTOR . '/stopapp/' . $this->aid, 
            array(), false, $this->uid);

        if (!json_decode($res)) {
            throw new Exception('Error terminating application '. $this->aid);
        }
    }
}
?>