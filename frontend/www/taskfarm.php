<?php
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
<script src="js/user.js"></script>
</head>
<body>
<script type="text/javascript">

	  	var sid = <?php echo $sid; ?>;
  		/* core functionality */
		function isStableState(state) {
			return state == 'INIT' || state == 'RUNNING' ||
				state == 'STOPPED' || state == 'ERROR';
		}

  		var poll_success_cb = null;
  		var poll_success_cb_param = null;
  		var poll_error_cb = null;

  		function pollState(delay) {
  	  		delay = (typeof delay == 'undefined') ? 1000 : delay + 1000;
  	  		count = delay / 1000;
  	  		showLoading(true, 'executing, please wait...');
		  	$.ajax({
			  	url: 'ajax/getState.php?sid=<?php echo $sid;?>',
			  	dataType: 'json',
			  	type: 'get',
		  		success: function (response) {
			  		if (typeof response.error != 'undefined') {
				  		showLoading(false);
				  		if (poll_error_cb != null) {
					  		poll_error_cb(response.error);
				  		} else {
				  			alert('pollState() error: ' + response.error);
				  		}
				  		return;
			  		}
					if (typeof response.state != 'undefined') {
						if (isStableState(response.state)) {
							showLoading(false);
							freezeInput(false);
							if (poll_success_cb != null) {
								poll_success_cb(poll_success_cb_param);
								poll_success_cb = null;
								poll_error_cb = null;
								poll_success_cb_param = null;
							}
						} else {
							setTimeout('pollState(' + delay + ');', delay);
						}
					}
		  		},
		  		error: function() {
			  		showLoading(false);
			  		alert('pollState(): Error loading the state');
		  		}
		  	});
  		}

		function showLoading(show, msg) {
			show = (typeof show == 'undefined') ? true : show;
			msg = (typeof msg == 'undefined') ? 'loading...' : msg;

			if (show) {
				$('#loading b').html(msg);
				$('#loading').show();
			} else {
				$('#loading').hide();
			}
		}

  		function freezeInput(freeze) {
  	  		buttonsSelector = '#startSample, #startExec';
  	  		if (freeze) {
  	  			$(buttonsSelector).attr('disabled', 'disabled');
  	  		} else {
  	  	  		$(buttonsSelector).removeAttr('disabled');
  	  		}
  		}

  		/*
  		 * make request that places the service into transient states, so it
  		 * may need polling
  		 * fields: params: {url, method, success, error, status, poll}
  		 */
  		function transientRequest(params) {
  	  		params.method =
  	  	  		(typeof params.method == 'undefined') ? 'get' : params.method;
	  	  	params.success =
  	  	  		(typeof params.success == 'undefined') ? null : params.success;
	  	  	params.error =
		  	  	(typeof params.error == 'undefined') ? null : params.error;
	  	  	params.poll =
		  	  	(typeof params.poll == 'undefined') ? true : params.poll;
			params.data =
		  	  	(typeof params.data == 'undefined') ? {} : params.data;

  	  		freezeInput(true);
  	  		showLoading(true, params.status);
  	  		$.ajax({
  	  	  		url: params.url, type: params.method, dataType: 'json',
  	  	  		data: params.data,
  	  	  		success: function(response) {
  	  	  	  		if (typeof response.error != 'undefined' && response.error != null ) {
  	  	  	  	  		freezeInput(false);
  	  	  	  	  		showLoading(false);
  	  	  	  	  		if (params.error != null) {
  	  	  	  	  	  		params.error(response.error);
  	  	  	  	  		} else {
  	  	  	  	  			alert('transientRequest() error: ' + response.error);
  	  	  	  	  		}
  	  	  	  	  		return;
  	  	  	  		}
  	  	  	  		if (typeof params.poll != 'undefined' &&
  	    	  	  	  		params.poll == true) {
  	  	  	  	  		poll_success_cb = params.success;
  	  	  	  	  		poll_error_cb = params.error;
  	  	  	  	  		poll_success_cb_param = response;
  	  	  	  	  		pollState();
  	  	  	  	  		return;
  	  	  	  		}
  	  	  	  		freezeInput(false);
  	  	  	  		showLoading(false);
  	  	  	  		if (params.success != null) {
  	  	  	  			params.success(response);
  	  	  	  		}
  	  	  		},
  	  	  		error: function(response) {
  	  	  	  		freezeInput(false);
  	  	  	  		showLoading(false);
  	  	  	  		alert('transientRequest(): Error sending the request');
  	  	  		}
  	  		});
  		}
</script>

<?php echo $page->renderHeader(); ?>
<?php echo PageStatus()->setId('loading'); ?>

	<div class="pagecontent">
	<?php echo $page->renderTopMenu(); ?>

<script>
$(document).ready(function() {
	$('#name').click(function() {
		newname = prompt("Enter a new name", $('#name').html());
		if (newname != null && newname != "") {
			$.ajax({
				url: 'ajax/saveName.php?sid='+sid,
				type: 'post',
				dataType: 'json',
				data: {
					name: newname,
				},
				success: function(response) {
					if (response.save == 1) {
						$('#name').html(newname);
					}
				}
			 });
		 }
	  });

	$('#terminate').click(function() {
		if (!confirm('After termination, the service will be completely'
				+ ' destroyed. Are you sure you want to continue?')) {
			return;
		}
		transientRequest({
			url: 'ajax/terminateService.php?sid='+sid,
			method: 'post',
			success: function(response) {
				window.location = 'index.php';
			},
			status: 'terminating service...',
			poll: false
		});
	});

});
</script>

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
		<script type="text/javascript">

			$(document).ready(function() {
				$('#fileForm').ajaxForm({
					dataType: 'json',
					success: function(response) {
						$('.additional .loading').toggleClass('invisible');
						if (typeof response.error != 'undefined' && response.error != null) {
							alert('Error: ' + response.error);
							$('#botFile').val('');
							$('#xmlFile').val('');
							return;
						}
						$('.additional .positive').show();
						setTimeout('$(".additional .positive").fadeOut();', 1000);
						// request ended ok
						$('#botFile').val('');
						$('#xmlFile').val('');
						// poll sample phase
						poll_success_cb = function (param) {
							window.location.reload();
						}
						freezeInput(true);
						pollState();
					},
					error: function(error) {
						alert('#fileForm.ajaxForm() error: ' + response.error);
					}
				});

				$('#startSample').click(function() {
					if ($('#botFile').val() == '') {
						alert('Please choose a .bot file');
						return;
					}
					if ($('#xmlFile').val() == '') {
						alert('Please choose a .xml file');
						return;
					}
					$('.additional .loading').toggleClass('invisible');
					$('#fileForm').submit();
				});
			});

		</script>
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

	<script type="text/javascript">
    	google.load('visualization', '1.0', {'packages':['corechart']});
		var samplingResults = null;
		var chart = null;

		function executionScheduleSelected(e) {
			selectedSampling = samplingResults[$('#samplings').attr('selectedIndex')];
			scheduleIndex = chart.getSelection()[0].row;
			$('#scheduleDetails').html(selectedSampling.schedules[scheduleIndex]);
			console.log(scheduleIndex);
		}

		function drawChart(schedules) {
			var data = new google.visualization.DataTable();
			data.addColumn('number', 'Execution Time');
			data.addColumn('number', 'Cost');
			$.each(schedules, function (index, schedule) {
				budget = parseInt(schedule.split('\t')[1]);
				console.log(schedule.split('\t'));
				data.addRow([(index + 1) * 15, budget]);
			});
	        var options = {
	        	width: 400, height: 240,
	        	title: 'Execution Options',
	        	pointSize: 3,
	        	hAxis: {
		        	title: 'Time Needed (minutes)',
		        	minValue: 0
		        },
		        vAxis: {
			        title: 'Budget/Cost'
		        }
	        };
	        chart = new google.visualization.LineChart(document.getElementById('executionChart'));
	        google.visualization.events.addListener(chart, 'select', executionScheduleSelected);
	        chart.draw(data, options);
		}

		function loadSamplingResults() {
			$.ajax({
				url: 'ajax/taskfarm_getSamplingResults.php?sid=' + sid,
				type: 'get',
				dataType: 'json',
				success: function(response) {
					if (typeof response.error != 'undefined' && response.error != null) {
						alert('Error loading sampling results: ' + response.error);
						return;
					}
					samplingResults = response;
					$('#samplings').empty();
					$.each(samplingResults, function (index, sampling) {
						$('#samplings').append($("<option></option>")
							.attr("value", sampling.timestamp)
							.text(sampling.name));
					});
					updateExecutionOptions();
				}
			});
		}

		function updateExecutionOptions() {
			selectedSampling = $('#samplings').attr('selectedIndex');
			options = samplingResults[selectedSampling].schedules;
			drawChart(options);
		}

		$(document).ready(function() {

			$('#samplings').change(function() {
				updateExecutionOptions();
			});

			$('#startExec').click(function() {
				if (chart.getSelection().length == 0) {
					alert('Please select an execution option');
					return;
				}
				executionOption = chart.getSelection()[0];
				$.ajax({
					url: 'ajax/taskfarm_runExecution.php',
					type: 'post',
					data: {
						sid: sid,
						schedulesFile: samplingResults[$('#samplings').attr('selectedIndex')].timestamp,
						scheduleNo: executionOption.row
					},
					dataType: 'json',
					success: function(response) {
						if (typeof response.error != 'undefined' && response.error != null) {
							alert('Error running execution: ' + response.error);
							return;
						}
						console.log("execution started");
						pollState();
					}
				});
			});

			loadSamplingResults();
		});
	</script>
	<?php endif; ?>
	<?php if (!$service->isStable()): ?>
		<script type="text/javascript">
			freezeInput(true);
			pollState();
		</script>
	<?php endif; ?>

<?php else: ?>
	<div class="box infobox">
		You cannot configure the service in the current state - <i> unreachable</i>.
		Please contact the system administrator.
	</div>
<?php endif; ?>

</div>
<?php echo $page->renderFooter(); ?>
</body>
</html>
