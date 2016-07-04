
/* Copyright (C) 2010-2013 by Contrail Consortium. */



manifest = [];

// manifest['owncloud'] = '{ "Application" : "New OwnCloud application", "Services" : [ { "Type" : "xtreemfs", "ServiceName" : "XtreemFS service", "Start" : 1, "VolumeStartup" : { "volumeName" : "data", "owner" : "www-data" } }, { "Type" : "mysql", "ServiceName" : "MySQL service", "Start" : 1, "Dump" : "https://online.conpaas.eu/owncloud/owncloud.sql", "Password" : "contrail123" }, { "Type" : "php", "ServiceName" : "PHP service", "Start" : 1, "Archive" : "https://online.conpaas.eu/owncloud/owncloud.tar.bz2", "StartupScript" : "https://online.conpaas.eu/owncloud/owncloud-startup.sh" } ]  }';

manifest['wordpress'] = '{ "Application" : "New Wordpress application", "Services" : [ { "Type" : "xtreemfs", "ServiceName" : "XtreemFS service", "Start" : 1, "VolumeStartup" : { "volumeName" : "data", "owner" : "www-data" } }, { "Type" : "mysql", "ServiceName" : "MySQL service", "Start" : 1, "Dump" : "https://online.conpaas.eu/wordpress/wordpress.sql", "Password" : "contrail123" }, { "Type" : "php", "ServiceName" : "PHP service", "Start" : 1, "Archive" : "https://online.conpaas.eu/wordpress/wordpress.tar.gz", "StartupScript" : "https://online.conpaas.eu/wordpress/wordpress.sh" } ]  }';

manifest['mediawiki'] = '{ "Application" : "New MediaWiki application", "Services" : [ { "Type" : "xtreemfs", "ServiceName" : "XtreemFS service", "Start" : 1, "VolumeStartup" : { "volumeName" : "data", "owner" : "www-data" } }, { "Type" : "mysql", "ServiceName" : "MySQL service", "Start" : 1, "Dump" : "https://online.conpaas.eu/mediawiki/mediawiki.sql", "Password" : "contrail123" }, { "Type" : "php", "ServiceName" : "PHP service", "Start" : 1, "Archive" : "https://online.conpaas.eu/mediawiki/mediawiki.tar.gz", "StartupScript" : "https://online.conpaas.eu/mediawiki/mediawiki.sh" } ]  }';


$(document).ready(function() {
	$('input:file').change(function() {
		$('input[name=type]').attr('checked', false);
	});

	$('input[name=type]').change(function() {
		$('input:file').val('');
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
		if ($('input:file').val() != '') {
			$('#fileForm').ajaxForm({
				data: {
					cloud: $('input[name=available_clouds]:checked').val()
				},
				dataType: 'json',
				success: function(response) {
					if (typeof response.error != 'undefined' && response.error != null) {
						alert('Error: ' + response.error);
						$('input:file').val('');
						$('input[name=type]').attr('checked', false);
						return;
					}
					alert("The manifest was correctly uploaded. Now it can take a while to start everything.")
					window.location = 'services.php?aid=' + response.aid;
				},
				error: function(response) {
					alert('#fileForm.ajaxForm() error: ' + response.error);
				}
			});

			$('#fileForm').submit();
			return;
		}

		type = $('input[name=type]:checked').val();
		if (type == undefined) {
			alert("Please upload a file or select a ready-made application to continue.");
			return;
		}

		if (manifest[type] == '') {
			alert("There is no manifest for this application.");
			return;
		}

		$.ajax({
			type: "POST",
			url: "ajax/uploadManifest.php",
			data: {
				json: manifest[type],
				cloud: $('input[name=available_clouds]:checked').val()
			},
			dataType: 'json'
		}).done(function(response) {
			if (typeof response.error != 'undefined' && response.error != null) {
				alert('Error: ' + response.error);
				$('input:file').val('');
				$('input[name=type]').attr('checked', false);
				return;
			}
			alert("The manifest was correctly uploaded. Now it can take a while to start everything.")
			window.location = 'services.php?aid=' + response.aid;
		});

	});

	$('.createpage .form .service').click(function () {
		$(this).find(':radio').attr('checked', true);
	});
});
