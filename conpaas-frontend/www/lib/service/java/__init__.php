<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('service');
require_module('ui/instance/java');

class JavaService extends Service {

	public function __construct($data, $manager) {
		parent::__construct($data, $manager);
	}

	public function hasDedicatedManager() {
		return true;
	}

	public function sendConfiguration($params) {
		return $this->managerRequest('post', 'update_java_configuration',
			$params);
	}

	public function createInstanceUI($node) {
		$info = $this->getNodeInfo($node);
		return new JavaInstance($info);
	}

	public function getInstanceRoles() {
		return array('proxy', 'web', 'backend');
	}
}

?>
