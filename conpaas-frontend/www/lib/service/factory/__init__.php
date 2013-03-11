<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

require_module('cloud');

class ServiceFactory {

	public static function createManager($service_data) {
		return new Manager($service_data);
	}

	public static function create($service_data) {
		$type = $service_data['type'];
		$manager = self::createManager($service_data);

		switch ($type) {
			case 'php':
				require_module('service/php');
				return new PHPService($service_data, $manager);
			case 'java':
				require_module('service/java');
				return new JavaService($service_data, $manager);
			case 'mysql':
				require_module('service/mysql');
				return new MysqlService($service_data, $manager);
			case 'taskfarm':
				require_module('service/taskfarm');
				return new TaskFarmService($service_data, $manager);
			case 'scalaris':
				require_module('service/scalaris');
				return new ScalarisService($service_data, $manager);
			case 'hadoop':
				require_module('service/hadoop');
				return new HadoopService($service_data, $manager);
			case 'xtreemfs':
				require_module('service/xtreemfs');
				return new XtreemFSService($service_data, $manager);
			case 'selenium':
				require_module('service/selenium');
				return new SeleniumService($service_data, $manager);
			case 'cds':
				require_module('service/cds');
				return new ContentDeliveryService($service_data, $manager);
			case 'htcondor':
				require_module('service/htcondor');
				return new HTCondorService($service_data, $manager);
/* BLUE_PRINT_INSERT		do not remove this line: it is a placeholder for installing new services */
			default:
				throw new Exception('Unknown service type');
		}
	}
}

?>
