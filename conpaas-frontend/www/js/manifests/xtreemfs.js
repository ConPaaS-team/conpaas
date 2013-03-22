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


function xtreemfs_pollNodesRunning(id) {
	$.ajax({
		url: 'ajax/getService.php?sid='+services[id].sid,
		dataType: 'json',
		success: function(service) {
			if (service.state == 'RUNNING') {
				done();
			} else {
				setTimeout('xtreemfs_pollNodesRunning('+id+');', 5000);
			}
		}
	});
}

function xtreemfs_addNodes(id) {
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

			xtreemfs_pollNodesRunning(id);
		}
	});
}

function xtreemfs_pollNodesRunningVolume(id) {
	$.ajax({
		url: 'ajax/getService.php?sid='+services[id].sid,
		dataType: 'json',
		success: function(service) {
			if (service.state == 'RUNNING') {
				xtreemfs_addNodes(id)
			} else {
				setTimeout('xtreemfs_pollNodesRunningVolume('+id+');', 5000);
			}
		}
	});
}


function xtreemfs_addVolume(id) {
	$('#status').html('Creating volume...');

	if (typeof services[id].VolumeStartup == 'undefined') {
		done();
		return;
	}

	$.ajax({
		url: 'ajax/createVolume.php',
		type: 'post',
		dataType: 'json',
		data: {
			sid: services[id].sid,
			volumeName: services[id].VolumeStartup.volumeName,
			owner: services[id].VolumeStartup.owner,
		},
		success: function(response) {
			checkErrors(response);

			xtreemfs_pollNodesRunningVolume(id);
		}
	});

}

function xtreemfs_pollServiceRunning(id) {
	$.ajax({
		url: 'ajax/getService.php?sid='+services[id].sid,
		dataType: 'json',
		success: function(service) {
			if (service.state == 'RUNNING') {
				xtreemfs_addVolume(id);
			} else {
				setTimeout('xtreemfs_pollServiceRunning('+id+');', 5000);
			}
		}
	});
}

function xtreemfs_startService(id) {
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

			xtreemfs_pollServiceRunning(id);
		}
	});
}

function xtreemfs_setFrontendName(id) {
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

			xtreemfs_startService(id);
		}
	});
}

function xtreemfs_pollService(id) {
	$.ajax({
		url: 'ajax/getService.php?sid='+services[id].sid,
		dataType: 'json',
		success: function(service) {
			if (service.state == 'INIT' && service.reachable == true) {
				xtreemfs_setFrontendName(id);
			} else {
				setTimeout('xtreemfs_pollService('+id+');', 5000);
			}
		}
	});
}

function xtreemfs_start(id) {
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
				xtreemfs_pollService(id);
			}
		}
	})
}
