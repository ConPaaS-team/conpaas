<?php

class Color {

	public static function getRoleColor($role) {
		return array(
			// application manager
			'manager' => '#333333',

			// web services (php / java)
			'backend' => '#0C72BA',//'#4F5B93',
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

}
