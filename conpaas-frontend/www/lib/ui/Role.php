<?php

class Role {

	public static function getColor($role) {
		return array(
			// application manager
			'manager' => '#333333',

			// web services (php / java)
			'backend' => '#0C72BA',
			'php' => '#4F5B93',
			'java' => '#0C72BA',
			'web' => '#E32C2E',
			'proxy' => '#149639',

			// mysql
			'mysql'=>'#f59620',
			'glb'=>'#3e78a6',

			// xtreemfs
			'dir' => '#333333',
			'mrc' => '#314E7E',
			'osd' => '#0088cc',

			// generic
			'master' => '#262E38',
			'node'=>'#496480',

			// outdated / unused
			'nodes'=>'orange',
			'peers' => 'blue',
			'masters' => 'blue',
			'slaves' => 'orange',
			'workers' => 'orange',
			'scalaris' => 'blue'
		)[$role];
	}

	public static function getText($role) {
		return array(
			// application manager
			'manager' => '&nbsp;&nbsp;&nbsp;Application manager&nbsp;&nbsp;&nbsp;',

			// web services (php / java)
			'backend' => 'backend',
			'php' => 'php',
			'java' => 'java',
			'web' => 'web',
			'proxy' => 'proxy',

			// mysql
			'mysql'=>'MySQL',
			'glb'=>'GLB',

			// xtreemfs
			'dir' => 'DIR',
			'mrc' => 'MRC',
			'osd' => 'OSD',

			// generic
			'master' => 'master',
			'node'=>'node',

			// outdated / unused
			'nodes'=>'nodes',
			'peers' => 'peers',
			'masters' => 'masters',
			'slaves' => 'slaves',
			'workers' => 'workers',
			'scalaris' => 'scalaris'
		)[$role];
	}

	public static function getInfo($role) {
		return array(
			// application manager
			'manager' => '',

			// web services (php / java)
			'backend' => '',
			'php' => 'PHP server',
			'java' => 'Apache Tomcat servlet container',
			'web' => 'static web server (Nginx)',
			'proxy' => 'load balancer (Nginx)',

			// mysql
			'mysql'=>'MySQL with Galera extensions',
			'glb'=>'Galera Load Balancer',

			// xtreemfs
			'dir' => 'XtreemFS Directory service',
			'mrc' => 'XtreemFS Metadata and Replica catalog',
			'osd' => 'XtreemFS Object Storage Device',

			// generic
			'master' => 'generic master node',
			'node'=>'generic regular node',

			// outdated / unused
			'nodes'=>'',
			'peers' => '',
			'masters' => '',
			'slaves' => '',
			'workers' => '',
			'scalaris' => ''
		)[$role];
	}

}
