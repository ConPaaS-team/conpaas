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

class Manager {

	protected $sid;
	protected $vmid;
	private $instance_type;
	private $service_type;

	public function __construct($data) {
		$this->service_type = $data['type'];
		$this->sid = $data['sid'];
		$this->vmid = $data['vmid'];
	}

	public function createContextFile($cloud) {
		$type = $this->service_type;
		$service_id = $this->sid;
		$root_dir = Conf::CONF_DIR;
		$cloud_scripts_dir = $root_dir.'/scripts/cloud';
		$cloud_cfg_dir = $root_dir.'/config/cloud';
		$mngr_cfg_dir = $root_dir.'/config/manager/';
		$mngr_scripts_dir = $root_dir.'/scripts/manager/';

		$frontend = Conf::getFrontendURL();

		// Get contextualization script for the cloud
		$cloud_script = file_get_contents($cloud_scripts_dir.'/'.$cloud);
		if ($cloud_script === false) {
			throw new Exception('Could not read the contextualization script '
				.'for the cloud: '.$cloud_scripts_dir.'/'.$cloud);
		}

		// Get manager setup file
		$mngr_setup = file_get_contents($mngr_scripts_dir.'/manager-setup');
		if ($mngr_setup === false) {
			throw new Exception('Could not read the manager setup file: '.
				$mngr_scripts_dir.'/manager-setup');
		}
		$mngr_setup = str_replace(array('%FRONTEND_URL%', '%CLOUD%'),
			array($frontend, $cloud),
			$mngr_setup);

		// Get cloud config file (could be multiple clouds - TODO)
		$cloud_cfg = file_get_contents($cloud_cfg_dir.'/'.$cloud.'.cfg');
		// TODO: support multiple clouds
		if ($cloud_cfg === false) {
			throw new Exception('Could not read cloud config file: '
				.$cloud_cfg_dir.'/'.$cloud.'.cfg');
		}

		// Get manager config file - add to the default one the one specific
		// to the service if it exists
		$mngr_cfg = file_get_contents($mngr_cfg_dir.'/default-manager.cfg');
		if (file_exists($mngr_cfg_dir.'/'.$type.'-manager.cfg')) {
			$mngr_cfg .= "\n".file_get_contents($mngr_cfg_dir.'/'.$type
				.'-manager.cfg');
		}

		if ($mngr_cfg  === false) {
			throw new Exception('Could not read manager config file');
		}

		$mngr_cfg = str_replace(array('%FRONTEND_URL%', '%CONPAAS_SERVICE_ID%',
				'%CONPAAS_SERVICE_TYPE%'),
			array($frontend, $service_id, $type),
			$mngr_cfg);

		if (file_exists($mngr_scripts_dir.'/'.$type.'-manager-start')) {
			$mngr_start_script = file_get_contents($mngr_scripts_dir.'/'.$type
				.'-manager-start');
		}
		else {
			$mngr_start_script = file_get_contents($mngr_scripts_dir
				.'/default-manager-start');
		}

		if ($mngr_start_script  === false) {
			throw new Exception('Could not read manager start script');
		}

		// Concatenate these
		$user_data = $cloud_script."\n\n";
		$user_data .= $mngr_setup."\n\n";
		$user_data .= "cat <<EOF > \$ROOT_DIR/config.cfg"."\n";
		$user_data .= $cloud_cfg."\n";
		$user_data .= $mngr_cfg."\n". "EOF"."\n\n";
		$user_data .= $mngr_start_script."\n";

		return $user_data;
	}
}
