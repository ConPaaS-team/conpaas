<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('logging');
require_module('service');
require_module('service/factory');
require_module('ui/instance/php');

class GenericService extends Service {
	public function __construct($data, $manager) {
		parent::__construct($data, $manager);
	}

}

?>