
/* Copyright (C) 2010-2013 by Contrail Consortium. */



manifest = [];

manifest['owncloud'] = '{ "Application" : "New OwnCloud application", "Services" : [ { "Type" : "xtreemfs", "ServiceName" : "XtreemFS service", "Start" : 1, "VolumeStartup" : { "volumeName" : "data", "owner" : "www-data" } }, { "Type" : "mysql", "ServiceName" : "MySQL service", "Start" : 1, "Dump" : "https://online.conpaas.eu/owncloud/owncloud.sql", "Password" : "contrail123" }, { "Type" : "php", "ServiceName" : "PHP service", "Start" : 1, "Archive" : "https://online.conpaas.eu/owncloud/owncloud.tar.bz2", "StartupScript" : "https://online.conpaas.eu/owncloud/owncloud-startup.sh" } ]  }';

manifest['wordpress'] = '{ "Application" : "New Wordpress application", "Services" : [ { "Type" : "xtreemfs", "ServiceName" : "XtreemFS service", "Start" : 1, "VolumeStartup" : { "volumeName" : "data", "owner" : "www-data" } }, { "Type" : "mysql", "ServiceName" : "MySQL service", "Start" : 1, "Dump" : "https://online.conpaas.eu/wordpress/wordpress.sql", "Password" : "contrail123" }, { "Type" : "php", "ServiceName" : "PHP service", "Start" : 1, "Archive" : "https://online.conpaas.eu/wordpress/wordpress.tar.gz", "StartupScript" : "https://online.conpaas.eu/wordpress/wordpress.sh" } ]  }';

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
