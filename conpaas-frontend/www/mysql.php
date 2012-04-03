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
require_module('ui/page/mysql');
require_module('ui/service');

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

$page = new MysqlPage($service);

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
<title>ConPaaS - configure Scalarix Service</title>
<link type="text/css" rel="stylesheet" href="conpaas.css" />
<?php echo $page->renderIcon(); ?>
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
	<?php if ($service->getNodesCount() > 0): ?>
	<div class="form-section">
		<div id="instancesWrapper">
			<?php echo $page->renderInstances(); ?>
		</div>
		<div class="actionstitle">add or remove instances to your deployment</div>
		<div class="actionsbar">
			<div class="tag blue"> <b id="slaves" class="editable" title="click to edit">0</b> DB Slave</div>
			<input type="button" id="submitnodes" value="submit" disabled="disabled" />
			<img class="loading" src="images/icon_loading.gif" style="display: none;" />
		</div>
	</div>
	<?php else: ?>
	<div class="box infobox">
		No instances are running
	</div>
	<?php endif; ?>

	<?php echo $page->renderAccessForm(); ?>
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
<script type="text/javascript" src="js/mysql.js"></script>
</body>
</html>
