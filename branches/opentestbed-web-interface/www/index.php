<?php 

require_once('__init__.php');
require_once('logging.php');
require_once('Page.php');
require_once('ServicesListUI.php');
require_once('ServiceData.php');

$page = new Page();
$services = ServiceData::getServicesByUser($page->getUID());
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
  	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />  	
    <title>ConPaaS - management interface </title>
    <link type="text/css" rel="stylesheet" href="conpaas.css" />
	<script src="js/jquery-1.5.js"></script>
	<script src="js/user.js"></script>
  </head>
  <body class="<?php echo $page->getBrowserClass(); ?>">

	<?php echo $page->renderHeader(); ?>  	
  	<div class="content">
  		<div class="pageheader">
  			<h1>Dashboard</h1>
  			<div class="menu">
  				<a class="button" href="create.php">+ create service</a>
  			</div>
  			<div class="clear"></div>
  		</div>
  		
  		<?php if (count($services) > 0): ?>
  			<div id="servicesWrapper">
  			<?php 
  				$servicesList = new ServicesListUI($services);
  				echo $servicesList->render();
  			?>
  			</div>
  			<script type="text/javascript">
  				function refreshServices() {
  	  				$.ajax({
  	  	  				url: 'services/checkServices.php',
  	  	  				dataType: 'html',
  	  	  				success: function(response) {
  	  	  	  				$('#servicesWrapper').html(response);
  	  	  				}
  	  				});
  				}
  			</script>
  		<?php else: ?>
		<div class="box infobox">
			You have no services in the dashboard. Go ahead and <a href="create.php">create a service</a>. You may also find the <a href="http://www.conpaas.eu/?page_id=32">help</a> useful.
		</div>
  		<?php endif; ?>
  	</div>
  </body>
</html>
