<?php

class Role {

	public static function getColor($serviceType, $role) {
		return array(
			// application manager
			'manager' => array(
				'manager' => '#333333'
			),

			// php service
			'php' => array(
				'backend' => '#4F5B93',
				'web' => '#E32C2E',
				'proxy' => '#149639'
			),

			// java service
			'java' => array(
				'backend' => '#0C72BA',
				'web' => '#E32C2E',
				'proxy' => '#149639'
			),

			// mysql service
			'mysql' => array(
				'mysql' => '#f59620',
				'glb' => '#3e78a6'
			),

			// xtreemfs service
			'xtreemfs' => array(
				'dir' => '#333333',
				'mrc' => '#314E7E',
				'osd' => '#0088cc'
			),

			// generic service
			'generic' => array(
				'master' => '#262E38',
				'node' =>'#496480'
			),

			// flink service
			'flink' => array(
				'master' => '#A265CB',
				'worker' => '#E6526F'
			)
		)[$serviceType][$role];
	}

	public static function getText($serviceType, $role) {
		return array(
			// application manager
			'manager' => array(
				'manager' => '&nbsp;&nbsp;&nbsp;Application manager&nbsp;&nbsp;&nbsp;'
			),

			// php service
			'php' => array(
				'backend' => 'php',
				'web' => 'web',
				'proxy' => 'proxy'
			),

			// java service
			'java' => array(
				'backend' => 'java',
				'web' => 'web',
				'proxy' => 'proxy'
			),

			// mysql service
			'mysql' => array(
				'mysql' => 'MySQL',
				'glb' => 'GLB'
			),

			// xtreemfs service
			'xtreemfs' => array(
				'dir' => 'DIR',
				'mrc' => 'MRC',
				'osd' => 'OSD'
			),

			// generic service
			'generic' => array(
				'master' => 'master',
				'node' =>'node'
			),

			// flink service
			'flink' => array(
				'master' => 'master',
				'worker' => 'worker'
			)
		)[$serviceType][$role];
	}

	public static function getInfo($serviceType, $role) {
		return array(
			// application manager
			'manager' => array(
				'manager' => ''
			),

			// php service
			'php' => array(
				'backend' => 'PHP server',
				'web' => 'static web server (NGINX)',
				'proxy' => 'load balancer (NGINX)'
			),

			// java service
			'java' => array(
				'backend' => 'Apache Tomcat servlet container',
				'web' => 'static web server (NGINX)',
				'proxy' => 'load balancer (NGINX)'
			),

			// mysql service
			'mysql' => array(
				'mysql' => 'MySQL with Galera extensions',
				'glb' => 'Galera Load Balancer'
			),

			// xtreemfs service
			'xtreemfs' => array(
				'dir' => 'XtreemFS Directory service',
				'mrc' => 'XtreemFS Metadata and Replica catalog',
				'osd' => 'XtreemFS Object Storage Device'
			),

			// generic service
			'generic' => array(
				'master' => 'generic master node',
				'node' =>'generic regular node'
			),

			// flink service
			'flink' => array(
				'master' => 'Flink master running a JobManager',
				'worker' => 'Flink worker running a TaskManager'
			)
		)[$serviceType][$role];
	}

}
