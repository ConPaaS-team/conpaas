<?php

require_once('InputButton.php');
require_once('MapredPage.php');

$sid = $_GET['sid'];
$services = parse_ini_file('services/services.ini', true);
$service = $services[$sid];

$page = new MapredPage($service);
$state = $page->fetchState();

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>ConPaaS - configure Map-Reduce service</title>
<link type="text/css" rel="stylesheet" href="conpaas.css" />
<script src="js/jquery-1.5.js"></script>
<script src="js/jquery.form.js"></script>
</head>
<body>
	
  	<div class="header">
  		<a id="logo" href="index.php"></a>
  		<div class="user">
  			Claudiu Dan Gheorghe | <a href="#">settings</a>
  		</div>
  		<div class="clear"></div>
  	</div>
  	
	 <div class="loadingWrapper invisible">
	 	<b>loading...</b>
	  	<img class="loading" src="images/throbber-on-white.gif" />
	 </div>
  	<div class="content">
    	<div class="pageheader">
  			<h1>Configure Service</h1>
	  		<div class="menu">
	  			<div id="state" class="status <?php echo $page->renderStateClass($state); ?>">
	  				<?php echo $state; ?>
	  			</div>
	  			<?php echo $page->renderActions($state); ?>
	  		</div>
	  		<div class="clear"></div>
	  		
	  		<script type="text/javascript">

			function isTransientState(state) {
				return state == 'INIT' || 
					state == 'PROLOGUE' || 
					state == 'EPILOGUE';
			}

			function showLoading(msg) {
				$('.loadingWrapper b').html(msg);
				$('.loadingWrapper').removeClass('invisible');
			}

			function hideLoading() {
				if (!$('.loadingWrapper').hasClass('invisible')) {
					$('.loadingWrapper').addClass('invisible');
				}
			}
			
	  		var manager = '<?php echo $service['manager'];?>';
	 		var delay = 1000;
	  		function pollState() {
		  		delay += 1000;
		  		$.ajax({
			  			url: manager,
			  			data: {
				  			action: 'getState'
			  			},
			  			dataType: 'json',
			  			type: 'get',
		  				success: function (response) {
							if (typeof response.state != 'undefined') {
								if (!isTransientState(response.state)) {
									window.location.reload();
								} else {
									showLoading('Now in ' + response.state);
									setTimeout('pollState();', delay);
								}
							}
		  				}
		  		});
	  		}
	  		
	  		$(document).ready(function() {
		  		$('#stop').click(function() {
			  		ack = confirm('Are you sure you want to stop the service?');
			  		if (ack) {
				  		showLoading();
						$('.content input, .content select').attr('disabled', 'disabled');
				  		$.ajax({
					  		url: manager,
					  		type: 'POST',
					  		data: {
						  		action: 'shutdown'
						  	},
						  	dataType: 'json',
					  		success: function(response) {
						  		if (typeof response.error != 'undefined') {
							  		alert(response.error);
							  		hideLoading();
						  		} else {
							  		showLoading('Shutdown in progress...');
							  		pollState();
						  		}
					  		}
				  		});
			  		}
		  		});

		  		$('#start').click(function() {
		  			showLoading('Starting service...');
		  			$.ajax({
			  			url: manager,
			  			type: 'POST',
			  			data: {
				  			action: 'startup'
			  			},
			  			dataType: 'json',
			  			success: function(response) {
					  		if (typeof response.error != 'undefined') {
						  		alert(response.error);
						  		hideLoading();
					  		} else {
						  		showLoading('System setup...');
						  		pollState();
					  		}
			  			}
		  			});
		  		});
	  		});
	  		</script>
  		</div>
  		
  		<div class="form-section front-section">
  			<img class="stype" src="images/hadoop.png" />
	  		<table class="form">
	  			<tr>
	  				<td class="description">Service Name</td>
	  				<td class="input"><b><?php echo $service['name']?></b></td>
	  			</tr>
	  			<tr>
	  				<td class="description">Type</td>
	  				<td class="input"> Map-Reduce Hadoop Service 
	  				</td>
	  			</tr>
	  			<tr>
	  				<td class="description">Created on</td>
	  				<td class="input">
	  					<p class="timestamp"><?php echo $service['creation_date']?></p>
	  				</td>
	  			</tr>
	  		</table>
  		</div>
	  	<div class="clear"></div>

		<?php if ($page->is_transient($state)): ?>
		<div class="transient">
			<h3>Initializing...</h3>
			<img src="images/throbber_bar.gif" />
		</div>
		
		<script type="text/javascript">
		setTimeout('pollState();', 2000);
		</script>
		<?php endif; ?>


		<div class="form-section">
			<div class="form-header">
				<div class="title">Manage Map-Reduce Environment</div>
				<div class="clear"></div>
			</div>
			
			<div id="jarform" class="mrform">			
				<table cellspacing="10">
				<tr valign="top">
					<td class="action">add applications</td>
					<td>
					<input type="button" value="+ add jar" />
					<div class="hint">add a source package of your application</div>
					</td>
				</tr>
				<tr valign="top">
					<td class="action">move data</td>
					<td>
					<i>from</i>
					<select>
						<option>filesystem</option>
						<option>MySQL</option>
					</select>
					<i>to</i>
					<select>
						<option>hdfs</option>
					</select>
					</td>
					<td>
						<input type="text" size="30"/>
						<input type="button" value="+ launch data move" />
						<div class="hint">
							parameters for running the data move job
						</div>
					</td>
				</tr>
				</table>
			</div>	
			
		</div>

		<div class="form-section">
			<div class="form-header">
				<div class="title">Manage Map-Reduce jobs</div>
				<div class="clear"></div>
			</div>
			<div id="mrapp" class="mrform">
				<table cellspacing="10">
				<tr valign="top">
					<td class="action">submit job</td>
					<td>
						<i>bin/hadoop jar </i>
						<select>
							<option>wordcount.jar</option>
							<option>myapp.jar</option>
							<option>aggregatelogs.jar</option>
						</select>
					</td>
					<td>
						<input type="text" size="35" />
						<input type="button" value="+ submit job" />
						<div class="hint">
							arguments for your application. Example: input path, output path
						</div>
					</td>
				</tr>
				</table>
			</div>
			
			<div class="brief">all Map-Reduce jobs</div>
			<div class="joblist">
				<div class="mrjob">
					<div class="left jobicon">
						<img src="images/server-icon.png" />
					</div>
					<div class="left">
						<div class="title">Job #3</div>
						<div class="subtitle">Submitted 5 minutes ago</div>
					</div>
					<div class="left progress">
						<i>Map: 80% &middot Reduce: 20%</i>
						<img src="images/progress.png" />
					</div>
					<div class="right">
						<img src="images/active.png" /> <br />
						<a href="#">check status</a>
					</div>
					<div class="clear"></div>
				</div>
				<div class="mrjob">
					<div class="left jobicon">
						<img src="images/data-icon.png" />
					</div>
					<div class="left">
						<div class="title">Job #5</div>
						<div class="subtitle">Submitted 1 hour ago</div>
					</div>
					<div class="clear"></div>
				</div>
			</div>
			
			<hr size="1" />
		</div>

</body>
</html>
 