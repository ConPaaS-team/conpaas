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

function java_pollNodesRunning(id) {
	$.ajax({
		url: 'ajax/getService.php?sid='+services[id].sid,
		dataType: 'json',
		success: function(service) {
			if (service.state == 'RUNNING') {
				done();
			} else {
				setTimeout('java_pollNodesRunning('+id+');', 5000);
			}
		}
	});
}

function java_addNodes(id) {
	$('#status').html('Adding service nodes...');

	if (typeof services[id].StartupInstances == 'undefined') {
		done();
		return;
	}

	// Subtract 1 from all the instances number
	for (var k in services[id].StartupInstances) {
		if (services[id].StartupInstances[k] > 0)
			services[id].StartupInstances[k]--;
	}
	// Add the sid to the object
	services[id].StartupInstances["sid"] = services[id].sid;

	$.ajax({
		url: 'ajax/addServiceNodes.php',
		type: 'post',
		dataType: 'json',
		data: services[id].StartupInstances,
		success: function(response) {
			checkErrors(response);

			java_pollNodesRunning(id);
		}
	});
}

function java_pollServiceRunning(id) {
	$.ajax({
		url: 'ajax/getService.php?sid='+services[id].sid,
		dataType: 'json',
		success: function(service) {
			if (service.state == 'RUNNING') {
				java_addNodes(id);
			} else {
				setTimeout('java_pollServiceRunning('+id+');', 5000);
			}
		}
	});
}

function java_startService(id) {
	$('#status').html('Starting the service...');

	if (typeof services[id].Start == 'undefined') {
		done();
		return;
	}

	if (services[id].Start == 0) {
		done();
		return;
	}

	$.ajax({
		url: 'ajax/requestStartup.php',
		type: 'post',
		dataType: 'json',
		data: {
			sid: services[id].sid,
		},
		success: function(response) {
			checkErrors(response);

			java_pollServiceRunning(id);
		}
	});
}

function java_uploadStartup(id) {
	$('#status').html('Uploading startup script...');

	if (typeof services[id].StartupScript != 'undefined') {
		$.ajax({
			url: 'ajax/uploadStartupScript.php',
			type: 'post',
			dataType: 'json',
			data: {
				sid: services[id].sid,
				script: services[id].StartupScript,
			},
			success: function(response) {
				checkErrors(response);

				java_startService(id);
			}
		});
	} else {
		java_startService(id);
	}
}

function java_setCodeVerision(id, code) {
	$('#status').html('Updating configuration...');

	$.ajax({
		url: 'ajax/sendConfiguration.php',
		type: 'post',
		dataType: 'json',
		data: {
			sid: services[id].sid,
			codeVersionId: code,
		},
		success: function(response) {
                        checkErrors(response);

			java_uploadStartup(id);
		}
	});
}

function java_uploadCode(id) {
	$('#status').html('Uploading code...');

	if (typeof services[id].Archive != 'undefined') {
		$.ajax({
			url: 'ajax/uploadCodeVersion.php',
			type: 'get',
			dataType: 'json',
			data: {
				sid: services[id].sid,
				url: services[id].Archive,
			},
			success: function(response) {
				checkErrors(response);

				var o = JSON.parse(response);

				java_setCodeVerision(id, o.result.codeVersionId);
			}
		});
	} else {
		java_uploadStartup(id);
	}
}

function java_setFrontendName(id) {
	$('#status').html('Setting the frontend name...');

	$.ajax({
		url: 'ajax/saveName.php',
		type: 'post',
		dataType: 'json',
		data: {
			sid: services[id].sid,
			name: services[id].FrontendName,
		},
		success: function(response) {
                        checkErrors(response);

			java_uploadCode(id);
		}
	});
}

function java_pollService(id) {
	$.ajax({
		url: 'ajax/getService.php?sid='+services[id].sid,
		dataType: 'json',
		success: function(service) {
			if (service.state == 'INIT' && service.reachable == true) {
				java_setFrontendName(id);
			} else {
				setTimeout('java_pollService('+id+');', 5000);
			}
		}
	});
}

function java_start(id) {
	$('#status').html('Creating the service...');

	$.ajax({
		url: 'ajax/createService.php',
		type: 'post',
		dataType: 'json',
		data: {
			type: services[id].Type,
			cloud: services[id].Cloud,
		},
		success: function(response) {
			checkErrors(response);

			if (response.create == 1) {
				services[id].sid = response.sid;
				java_pollService(id);
			}
		}
	})
}
