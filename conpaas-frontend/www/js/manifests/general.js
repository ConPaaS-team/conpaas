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

/* This counter will increase every time a service will be
 * started and when it will goes back to 0 then return to
 * the index page.
 */
var service_up = 0;

/* This array contains objects of all the services that needs to be started.
 * Each object will contain the following arguments
 *
 *  frontendName
 *  type
 *  cloud
 *  sid
 */
var services = [ ];

/* If anything goes wrong, stop the animations and try again.
 */
function stop() {
	$('.loading').hide();
	$('#status').html('');
	$('#create').removeAttr('disabled');
}

function done() {
	service_up--;

	if (service_up == 0)
		window.location = 'services.php';
}

function checkErrors(response) {
	if (response.error != null) {
		alert(response.error);
		stop();
		done();
	}
}

function startServices(specs) {
	$('#file').val('');
	$('.loading').show();

	services = specs.Services;

	for (var id = 0 ; id < services.length ; id++) {
		service_up++;
		if (services[id].Type == "php") {
			php_start(id);
		} else if (services[id].Type == "java") {
			java_start(id);
		} else if (services[id].Type == "mysql") {
			mysql_start(id);
		} else if (services[id].Type == "scalaris") {
			scalaris_start(id);
		} else if (services[id].Type == "hadoop") {
			hadoop_start(id);
		} else if (services[id].Type == "selenium") {
			selenium_start(id);
		} else if (services[id].Type == "xtreemfs") {
			xtreemfs_start(id);
		} else if (services[id].Type == "taskfarm") {
			taskfarm_start(id);
		} else {
			alert("Error, type " + services[id].Type + " unknown");
			service_up--;
		}
	}

	if (service_up == 0)
		window.location = 'services.php';
}

$(document).ready(function() {
	$('#fileForm').ajaxForm({
		dataType: 'json',
		success: function(response) {
			if (typeof response.error != 'undefined' && response.error != null) {
				alert('Error: ' + response.error);
				$('#file').val('');
				return;
			}
			// request ended ok
			specs = JSON.parse(response.result);
			startServices(specs);
		},
		error: function(response) {
			alert('#fileForm.ajaxForm() error: ' + response.error);
		}
	});

	$('input:file').change(function() {
		$('#fileForm').submit();
	});
});
