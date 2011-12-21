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
require_module('ui/page');
require_module('ui/service');

$page = new Page();
$services = ServiceData::getServicesByUser($page->getUID());

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
  	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />  	
    <title>ConPaaS - management interface </title>
    <?php echo $page->renderIcon(); ?>
    <link type="text/css" rel="stylesheet" href="conpaas.css" />
	<script src="js/jquery-1.5.js"></script>
	<script src="js/user.js"></script>
  </head>
  <body class="<?php echo $page->getBrowserClass(); ?>">

	<?php echo $page->renderHeader(); ?>  	
  	<div class="pagecontent">
  		<div class="pageheader">
  			<h1> <img src="images/dashboard.png" /> Dashboard</h1>
  			<div class="menu">
  				<a class="button" href="create.php"> create service</a>
  			</div>
  			<div class="clear"></div>
  		</div>
  		
  		<?php if (count($services) > 0): ?>
  			<div id="servicesWrapper">
  			<?php
  				$serviceObjs = array();
				foreach ($services as $service_data) {
					$serviceObjs[] = ServiceFactory::create($service_data);
				}
  				$servicesList = new ServicesListUI($serviceObjs);
  				echo $servicesList->render();
  			?>
  			</div>
  			<script type="text/javascript">
  				function refreshServices() {
  	  				$.ajax({
  	  	  				url: 'ajax/checkServices.php',
  	  	  				dataType: 'html',
  	  	  				success: function(response) {
  	  	  	  				$('#servicesWrapper').html(response);
  	  	  				}
  	  				});
  				}

  				function onDeleteService(button) {
  					sid = $(button).attr('name');
  	  				$.ajax({
  	  	  				url: 'ajax/terminateService.php?sid=' + sid,
  	  	  				type: 'post',
  	  	  				dataType: 'json',
  	  	  				success: function(response) {
  	    	  	  	  		if (typeof response.error != 'undefined' && response.error != null ) {
  	  	    	  	  	  		alert('Error trying to remove service: ' + response.error);
  	    	  	  	  		}
  	    	  	  	  		$('#' + 'service-' + sid).hide();
  	  	  				}
	  	  			});
  				}
  			</script>
  		<?php else: ?>
		<div class="box infobox">
			You have no services in the dashboard. Go ahead and <a href="create.php">create a service</a>.
		</div>
  		<?php endif; ?>
  	</div>
  	<?php echo $page->renderFooter(); ?>
  </body>
</html>
