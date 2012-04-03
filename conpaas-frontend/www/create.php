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
require_module('ui/cloud');
require_module('ui/page');

$conf = Logging::loadConf();
$clouds = array(
	'ec2' => $conf['enable_ec2'] == "yes",
	'opennebula' => $conf['enable_opennebula'] == "yes",
);
$default_cloud = false;
foreach (array('ec2', 'opennebula') as $cloud) {
	if ($clouds[$cloud]) {
		$default_cloud = $cloud;
		break;
	}
}

$page = new Page();

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
  	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>ConPaaS - create new service </title>
    <link type="text/css" rel="stylesheet" href="conpaas.css" />
    <?php echo $page->renderIcon(); ?>
	<script src="js/jquery-1.5.js"></script>
	<script src="js/conpaas.js"></script>
  </head>
  <body class="<?php echo $page->getBrowserClass(); ?>">

	<?php echo $page->renderHeader(); ?>

  	<div class="pagecontent createpage">
    	<div class="pageheader">
  		</div>
		<div id="selectHint">
			please select one of the services below <img width="12px" src="images/lookdown.png" />
		</div>
  		<table class="form" cellspacing="0" cellpading="0">
  			<tr class="service">
  				<td class="description"> <img src="images/php.png" height="32" /></td>
  				<td class="radio" width="150px"><input type="radio" name="type" value="php" /> php</td>
  				<td class="info" width="480px"> PHP version 5.2 under Nginx </td>
  			</tr>
  			<tr class="service">
  				<td class="description"> <img src="images/java.png" height="32" /></td>
  				<td class="radio"><input type="radio" name="type" value="java" /> java</td>
  				<td class="info"> Java Servlet container using Apache Tomcat 7.2</td>
  			</tr>
  			<tr class="service">
  				<td class="description"> <img src="images/mysql.png" height="32" /></td>
  				<td class="radio"><input type="radio" name="type" value="mysql" /> mysql</td>
  				<td class="info"> MySQL 5.2 Database </td>
  			</tr>
  			<tr class="service">
  				<td class="description"> <img src="images/scalaris.png" height="32" /></td>
  				<td class="radio"><input type="radio" name="type" value="scalaris" /> scalaris</td>
  				<td class="info"> in-memory key-value storage </td>
  			</tr>
  			<tr class="service">
  				<td class="description"> <img src="images/hadoop.png" height="32" /></td>
  				<td class="radio"><input type="radio" name="type" value="hadoop" /> map-reduce</td>
  				<td class="info"> Hadoop MapReduce cluster </td>
  			</tr>
  			<tr class="service">
  				<td class="description"> <img src="images/taskfarm.png" height="32" /></td>
  				<td class="radio"><input type="radio" name="type" value="taskfarm" /> task farm</td>
  				<td class="info"> Service for running sets of tasks </td>
  			</tr>
  			<tr>
  				<td>&nbsp;</td>
  			</tr>
  			<tr>
  				<td class="description">cloud provider</td>
  				<td class="input">
  					<select id="cloud" style="height: 40px;" size="2">
  						<?php
  							echo CloudOption('opennebula', 'OpenNebula')
  								->setEnabled($clouds['opennebula'])
  								->setSelected($default_cloud == 'opennebula');
  							echo CloudOption('ec2', 'Amazon EC2')
  								->setEnabled($clouds['ec2'])
  								->setSelected($default_cloud == 'ec2');
  						?>
  					</select>
  				</td>
  				<td class="info">
  					only OpenNebula is enabled on this deployment
  				</td>
  			</tr>
  		</table>
  		<div class="createWrap">
			<a id="create" class="button" href="javascript: void(0);">
  				<img src="images/play.png" style="vertical-align: top;"/> create service
  			</a>
  			<div class="clear"></div>
		</div>
  	</div>
	<?php echo $page->renderFooter(); ?>
	<script type="text/javascript" src="js/servicepage.js"></script>
	<script type="text/javascript" src="js/create.js"></script>
  </body>
</html>
