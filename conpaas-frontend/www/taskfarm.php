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

require_once('__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('ui');
require_module('ui/page');
require_module('ui/page/taskfarm');
require_module('ui/service');

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

$page = new TaskFarmPage($service);

if ($service->getUID() !== $page->getUID()) {
    $page->redirect('index.php');
}

$state = $page->getState();
$backendType = $service->getType();

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Task Farm service</title>
<link type="text/css" rel="stylesheet" href="conpaas.css" />
<?php echo $page->renderIcon(); ?>
<script type="text/javascript" src="https://www.google.com/jsapi"></script>
<script src="js/jquery-1.5.js"></script>
<script src="js/jquery.form.js"></script>
<script src="js/conpaas.js"></script>
</head>
<body>

<?php echo $page->renderHeader(); ?>
<?php echo PageStatus()->setId('loading'); ?>

	<div class="pagecontent">
	<?php echo $page->renderTopMenu(); ?>

<?php if ($service->isConfigurable()): ?>

	<div class="form-section">
		<div class="form-header">
			<div class="title">Sampling</div>
			<div class="clear"></div>
		</div>

		<form id="fileForm" action="ajax/taskfarm_sample.php?sid=<?php echo $sid;?>">
  		<table class="form" cellspacing="0" cellpading="0">
  			<tr>
  				<td class="description">the *.bot file</td>
  				<td class="input">
				<input id="botFile" type="file" name="botFile" />
  				</td>
  				<td class="info">more info about .bot file</td>
  			</tr>
  			<tr>
  				<td class="description">configuration file</td>
  				<td class="input">
  				<input id="xmlFile" type="file" name="clusterFile" />
  				</td>
  				<td class="info"> XML file</td>
  			</tr>
  			<tr>
  				<td class="description">URL</td>
  				<td class="input">
  					<input type="text" name="uriLocation" />
  				</td>
  				<td class="info">
  					mount path for XtremeFS volume (optional)
  				</td>
  			</tr>
  			<tr>
  				<td class="description"></td>
  				<td><input type="button" value="Start sampling" id="startSample" />
				<div class="additional" style="display: inline;">
					<img class="loading invisible" src="images/icon_loading.gif" />
					<i class="positive" style="display: none;">Submitted successfully</i>
				</div>
  				</td>
  			</tr>
  		</table>
		</form>
		<div class="clear"></div>
	</div>

	<?php if ($service->hasSamplingResults()): ?>
	<div class="form-section">
		<div class="form-header">
			<div class="title">Execution</div>
			<div class="clear"></div>
		</div>

		<table class="form" id="botexec">
		<tr>
			<td class="description">schedule</td>
			<td class="input">
				<select id="samplings">
				</select>
			</td>
			<td class="input">
				<div id="executionChart">
				</div>
			</td>
		</tr>
		<tr>
			<td class="description"></td>
			<td class="input">
				<input id="startExec" type="button" value="Start execution"/>
			</td>
			<td>
				<div id="scheduleDetails">
					please click on the graph to select an execution
				</div>
			</td>
		</tr>
		</table>
	</div>

	<?php endif; ?>

<?php else: ?>
	<div class="box infobox">
		You cannot configure the service in the current state - <i> unreachable</i>.
		Please contact the system administrator.
	</div>
<?php endif; ?>

</div>
<?php echo $page->renderFooter(); ?>
<?php echo $page->generateJSGetParams(); ?>
<script type="text/javascript" src="js/servicepage.js"></script>
<script type="text/javascript" src="js/taskfarm.js"></script>
</body>
</html>
