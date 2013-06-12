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

manifest = [];

manifest['owncloud'] = '{ "Application" : "New OwnCloud application", "Services" : [ { "Type" : "xtreemfs", "ServiceName" : "XtreemFS service", "Start" : 1, "VolumeStartup" : { "volumeName" : "data", "owner" : "www-data" } }, { "Type" : "mysql", "ServiceName" : "MySql service", "Start" : 1, "Dump" : "https://online.conpaas.eu/owncloud/owncloud.sql", "Password" : "contrail123" }, { "Type" : "php", "ServiceName" : "PHP service", "Start" : 1, "Archive" : "https://online.conpaas.eu/owncloud/owncloud.tar.bz2", "StartupScript" : "https://online.conpaas.eu/owncloud/owncloud-startup.sh" } ]  }';
manifest['wordpress'] = '{ "Application" : "Wordpress", "Services" : [ { "Type" : "php", "ServiceName" : "Php backend", "Archive" : "http://wordpress.org/wordpress-3.5.1.tar.gz" }, { "Type" : "mysql", "ServiceName" : "Mysql backend" } ] }';

$(document).ready(function() {
	$('#fileForm').ajaxForm({
		dataType: 'json',
		success: function(response) {
			if (typeof response.error != 'undefined' && response.error != null) {
				alert('Error: ' + response.error);
				$('#file').val('');
				return;
			}
			alert("Manifest uploaded correctly, now it can take a while to startup everything")
			window.location = 'index.php';
		},
		error: function(response) {
			alert('#fileForm.ajaxForm() error: ' + response.error);
		}
	});

	$('input:file').change(function() {
		$('#fileForm').submit();
	});

    $('#logout').click(function () {
        $.ajax({
                type: 'POST',
                url: 'ajax/logout.php', 
                data: {}
        }).done(function () { 
            window.location = 'index.php'; 
        });       
    });

	$('#deploy').click(function() {
		type = $('input[name=type]:checked').val();
		if (manifest[type] == '') {
			alert("There is no manifest for such an application");
			return;
		}

		$.ajax({
			type: "POST",
			url: "ajax/uploadManifest.php",
			data: { json: manifest[type] },
			dataType: 'json'
		}).done(function(response) {
			if (typeof response.error != 'undefined' && response.error != null) {
				alert('Error: ' + response.error);
				$('#file').val('');
				return;
			}
			alert("Manifest uploaded correctly, now it can take a while to startup everything")
			window.location = 'index.php';
		});

	});
});
