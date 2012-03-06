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
require_module('ui/page/scalarix');
require_module('ui/service');

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);

$page = new ScalarixPage($service);

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
  	  		showLoading(true, 'performing changes - wait (' + count + ')...');
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
  	  		buttonsSelector = '#start, #stop, #terminate, #submitnodes, #file';
	  	  	linksSelector = '.versions .activate';
  	  		if (freeze) {
  	  			$(buttonsSelector).attr('disabled', 'disabled');
  	  			$(linksSelector).hide();
  	  		} else {
  	  	  		$(buttonsSelector).removeAttr('disabled');
  	  	  		$(linksSelector).show();
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

	$('#stop').click(function() {
  		ack = confirm('Are you sure you want to stop the service?');
  		if (ack) {
  	  		transientRequest({
  	  	  		url: 'ajax/requestShutdown.php?sid='+sid,
  	    	  	method: 'post',
  	    	  	success: function(response) {
  	    	  		window.location.reload();
  	    		},
  	    		status: 'stopping service...',
  	    		poll: true
  	  		});
  		}
	});

	$('#start').click(function() {
		transientRequest({
			url: 'ajax/requestStartup.php?sid='+sid,
			method: 'post',
			success: function(response) {
				window.location.reload();
			},
			status: 'starting service...',
			poll: true
		});
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
	<?php if ($service->isRunning()): ?>
	<script text="text/javascript">

	function reloadInstances() {
		$.ajax({
			url: 'ajax/render.php',
			data: { sid: sid, target: 'instances' },
			type: 'get',
			dataType: 'html',
			success: function(data) {
				$('#instancesWrapper').html(data);
			}
		});
	}

	function getInstancesParams(assoc) {
		if (assoc) {
			return {
				'scalarix': parseInt($('#scalarix').html())
			};
		}
		return [parseInt($('#scalarix').html())];
	}

	function changeInstances(action, params) {
		$('.actionsbar .loading').show();

		transientRequest({
			url: 'ajax/' + action + '.php?sid=' + sid,
			method: 'post',
			data: params,
			poll: true,
			status: 'adding/removing nodes...',
			success: function(response) {
				$('.actionsbar .loading').hide();
				reloadInstances();
				$('#scalarix').each(function() {
					$(this).html('0');
				});
				$('#submitnodes').attr('disabled', 'disabled');
			},
			error: function(error) {
				$('.actionsbar .loading').hide();
				alert('changeInstances() error: ' + error);
			}
		});
	}

	function enableChangeInstances() {
		params = getInstancesParams(false);
	  	for (i in params) {
		  	value = params[i];
		  	if (value != 0) {
			  	$('#submitnodes').removeAttr('disabled');
			  	return;
		  	}
	  	}
	  	$('#submitnodes').attr('disabled', 'disabled');
	}

	$(document).ready(function() {
		$('#submitnodes').click(function() {
			add = '';
			addParams = {};
			remove = '';
			removeParams = {};
			params = getInstancesParams(true);
			for (type in params) {
				addParams[type] = 0;
				removeParams[type] = 0;
				if (params[type] > 0) {
					if (add != '') {
						add += ' & ';
					}
					add += params[type] + ' ' + type;
					addParams[type] = params[type];
				} else if (params[type] < 0) {
					if (remove != '') {
						remove += ' & ';
					}
					remove += '' + (-params[type]) + ' ' + type;
					removeParams[type] = -params[type];
				}
			}
			msg = '';
			if (add != '') {
				msg = 'add ' + add + ' nodes';
			}
			if (remove != '') {
				if (msg != '') {
					msg += ' and to ';
				}
				msg += 'remove ' + remove + ' nodes';
			}
			ack = confirm('Are you sure you want to ' + msg + '?');
			if (ack) {
				if (add != '') {
					changeInstances('addServiceNodes', addParams);
				}
				if (remove != '') {
					changeInstances('removeServiceNodes', removeParams);
				}
			}
		});

		$('#scalarix').click(function() {
			value = prompt('no. of instances (e.g. +1, -2)', $(this).html());
			if (value != null && value != "") {
				intValue = parseInt(value);
				if (!isNaN(intValue)) {
					sign = (intValue > 0) ? '+' : '';
					$(this).html(sign + intValue);
					enableChangeInstances();
				}
			}
		});
	});
	</script>

	<div class="form-section">
		<div id="instancesWrapper">
			<?php echo $page->renderInstances(); ?>
		</div>
		<div class="actionstitle">add or remove instances to your deployment</div>
		<div class="actionsbar">
			<div class="tag blue"> <b id="scalarix" class="editable" title="click to edit">0</b> DB nodes</div>
			<input type="button" id="submitnodes" value="submit" disabled="disabled" />
			<img class="loading" src="images/icon_loading.gif" style="display: none;" />
		</div>
	</div>
	<?php else: ?>
	<div class="box infobox">
		No instances are running
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
</body>
</html>
