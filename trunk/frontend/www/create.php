<?php 

require_once('__init__.php');
require_once('logging.php');
require_once('Page.php');

$page = new Page();

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
  	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />  	
    <title>ConPaaS - create new service </title>
    <link type="text/css" rel="stylesheet" href="conpaas.css" />
	<script src="js/jquery-1.5.js"></script>
	<script src="js/user.js"></script>
  </head>
  <body class="<?php echo $page->getBrowserClass(); ?>">

	<?php echo $page->renderHeader(); ?>
	  	
  	<div class="content">
    	<div class="pageheader">
  			<h1>Create service</h1>
  			<div class="clear"></div>
  		</div>
  	
  		<table class="form">
  			<tr>
  				<td class="description">type of service</td>
  				<td class="input">
  					<select id="type" size="3">
  						<option value="php" selected="selected">PHP Service</option>
  						<option value="java">Java Service</option>
  						<option value="mysql" disabled="disabled">MySQL Service</option>
  						<option value="hadoop" disabled="disabled">Map-Reduce Service</option>
  					</select>
  				</td>
  				<td class="info">
  					for now only selectable services available
  				</td>
  			</tr>
  			<tr>
  				<td class="description">software version</td>
  				<td class="input">
  					<select id="version">
  						<option value="5.3">5.3</option>
  					</select>
  				</td>
  			</tr>
  			<tr>
  				<td class="description">cloud provider</td>
  				<td class="input">
  					<select id="cloud">
  						<option value="ec2" selected="selected">Amazon EC2</option>
  						<option value="opennebula">OpenNebula</option>
  					</select>
  				</td>  			
  			</tr>
  			<tr>
  				<td class="description" style="vertical-align: middle;">
  					<img class="loading" src="images/icon_loading.gif"
						 style="display: none;" />
  				</td>
  				<td class="input">
	  				<input id="create" type="button" value="create service"/>
  				</td>
  			</tr>
  			<tr>
  				<td class="description"></td>
  				<td>
  					<i id="status"></i>
  					<i id="error" style="display: none;"></i>
  				</td>
  			</tr>
  		</table>
  	</div>
	<script type="text/javascript">
		function pollService(sid) {
			$.ajax({
				url: 'services/getService.php?sid='+sid,
				dataType: 'json',
				success: function(service) {
					if (service.state != 3) {
						window.location = 'index.php';
					} else {
						setTimeout('pollService('+sid+');', 2000);
					}
				}
			});
		}

		$(document).ready(function() {
			$('#create').click(function() {
				$('.loading').show();
				$('#status').html('creating service...');
				$(this).attr('disabled', 'disabled');
				// sending request
				$.ajax({
					url: 'services/createService.php',
					type: 'post',
					dataType: 'json',
					data: {
						type: $("#type option:selected").val(), 
						sw_version: $("#version option:selected").val(),
						cloud: $('#cloud option:selected').val(),
					},
					success: function(response) {
						if (typeof response.error !== 'undefined') {
							alert(response.error);
							$('.loading').hide();
							$(this).removeAttr('disabled');
							return;
						}

						if (response.create == 1) {	
							$('#status').html('initializing...');
							pollService(response.sid);
						}
					}
				})
			});

		});
	</script>
  </body>
</html>
