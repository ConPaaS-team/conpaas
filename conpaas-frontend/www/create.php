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
		<div class="selectHint">
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
  				<td class="radio"><input type="radio" name="type" value="scalaris" /> scalarix</td>
  				<td class="info"> in-memory key-value store </td>
  			</tr>
  			<tr class="service">
  				<td class="description"> <img src="images/hadoop.png" height="32" /></td>
  				<td class="radio"><input type="radio" name="type" value="hadoop" /> map-reduce</td>
  				<td class="info"> Hadoop MapReduce cluster </td>
  			</tr>

	   			<tr class="service">
	   				<td class="description"> <img src="images/taskfarm.png" height="32" /></td>
	   				<td class="radio"><input type="radio" name="type" value="taskfarm" /> task farm</td>
	   				<td class="info"> Service for running bags of tasks </td>
	   			</tr>

  			<tr class="service">
  				<td class="description"> <img src="images/selenium.png" height="32" /></td>
  				<td class="radio"><input type="radio" name="type" value="selenium" /> selenium</td>
  				<td class="info"> Selenium functional testing service </td>
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
					<?php
						if ($default_cloud == 'ec2') {
							$cloud_text = 'Amazon EC2';
						}
						else {
							$cloud_text = 'OpenNebula';
						}
   						echo "Only $cloud_text is enabled on this deployment";
                                        ?>
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
