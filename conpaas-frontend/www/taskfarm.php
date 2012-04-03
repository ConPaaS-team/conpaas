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
