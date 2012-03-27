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
require_module('ui/service');

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

$page = new ServicePage($service);

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
<title>ConPaaS - configure PHP Service</title>
<link type="text/css" rel="stylesheet" href="conpaas.css" />
<?php echo $page->renderIcon(); ?>
<script src="js/jquery-1.5.js"></script>
<script src="js/jquery.form.js"></script>
<script src="js/conpaas.js"></script>
</head>
<body>

	<?php echo $page->renderHeader(); ?>
	<div class="pagecontent">
	<?php echo $page->renderTopMenu(); ?>

<?php if ($service->isConfigurable()): ?>
	<?php if ($service->getNodesCount() > 0): ?>
	<div class="form-section">
		<div id="instancesWrapper">
			<?php echo $page->renderInstances(); ?>
		</div>
		<div class="actionstitle">add or remove instances to your deployment</div>
		<div class="actionsbar">
			<div class="tag orange"> <b id="proxy" class="editable" title="click to edit">0</b> proxy</div>
			<div class="tag blue"> <b id="web" class="editable" title="click to edit">0</b> web</div>
			<div class="tag purple"> <b id="backend" class="editable" title="click to edit">0</b> <?php echo $backendType ?></div>
			<input type="button" id="submitnodes" value="submit" disabled="disabled" />
			<img class="loading" src="images/icon_loading.gif" style="display: none;" />
		</div>
	</div>
	<?php else: ?>
	<div class="box infobox">
		No instances are running
	</div>
	<?php endif; ?>

	<div class="form-section">
		<div class="form-header">
			<div class="title">Code management</div>
			<div class="access-box">
				<?php
				if ($service->isRunning()) {
					echo LinkUI('access application',
								$service->getAccessLocation())
								->setExternal(true);
				}
				?>
			</div>
			<div class="clear"></div>
		</div>
		<div id="deployform">
			<div class="deployoptions">
			<i>you may update the stage by</i>
				<div class="deployoption">
					<input type="radio" name="method" checked/>uploading archive
				</div>
			<i>or by</i>
			<div class="deployoption">
				<input type="radio" name="method" disabled="disabled" />checking out repository
			</div>
			</div>
			<div class="deployactions">

			<form id="fileForm" action="<?php echo $page->getUploadURL() ?>" enctype="multipart/form-data">
				<input id="file" type="file" name="code" />
				<input type="hidden" name="description" value="no description" />
			</form>
			<div class="additional">
				<img class="loading invisible" src="images/icon_loading.gif" />
					<i class="positive" style="display: none;">Submitted successfully</i>
				</div>
				<div class="clear"></div>
				<div class="hint">
					example: <b>.zip</b>, <b>.tar</b> of your source tree
				</div>

			</div>
			<div class="deployactions invisible">
				<input type="text" size="40" />
				<input type="button" value="checkout" />
				<div class="hint">
					example: <b>git checkout git@10.3.45.1:repos/</b>
				</div>
			</div>
			<div class="clear"></div>
		</div>
		<div class="brief">available code versions</div>
		<div id="versionsWrapper">
			<?php echo $page->renderVersions(); ?>
		</div>
	</div>

	<div class="form-section">
		<div class="form-header">
			<div class="title">Settings</div>
			<div class="clear"></div>
		</div>
	    <table class="form settings-form">
			<tr>
	  			<td class="description">Software version </td>
	  			<td class="input">
	  				<select onchange="confirm('Are you sure you want to change the software version?')">
	  					<option>5.3</option>
	  				</select>
	  			</td>
	  		</tr>
			<tr>
				<td class="description">Maximum script execution time</td>
				<td class="input">
	              <?php echo $page->renderExecTimeOptions(); ?>
				</td>
			</tr>
			<tr>
				<td class="description">Memory limit </td>
				<td class="input">
	              <?php echo $page->renderMemLimitOptions() ?>
				</td>
			</tr>
			<tr>
				<td class="description"></td>
				<td class="input actions">
					<input id="saveconf" type="button" disabled="disabled" value="save" />
					 <i class="positive" style="display: none;">Submitted successfully</i>
				</td>
			</tr>
		</table>
	</div>

	<?php if (!$service->isStable()): ?>
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
<script src="js/servicepage.js"></script>
<script src="js/hosting.js"></script>
</body>
</html>