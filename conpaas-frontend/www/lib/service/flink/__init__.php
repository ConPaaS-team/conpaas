<?php

require_module('http');
require_module('service');
require_module('logging');
require_module('ui/instance/flink');

class FlinkService extends Service {

    public function __construct($data, $manager) {
        parent::__construct($data, $manager);
    }

    public function fetchHighLevelMonitoringInfo() {
        return false;
    }

    public function getInstanceRoles() {
        return array('master', 'worker');
    }

    public function createInstanceUI($info) {
        return new FlinkInstance($info);
    }

    public function getMasterAddr() {
        $master_node = $this->getNodeInfo($this->nodesLists['master'][0]);
        return $master_node['ip'];
    }

    public function getAccessLocation() {
        return 'http://'.$this->getMasterAddr().':8081/';
    }

}

?>
