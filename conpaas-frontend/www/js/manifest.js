
/* Copyright (C) 2010-2013 by Contrail Consortium. */



manifest = [];

// manifest['owncloud'] = '{ "Application" : "New OwnCloud application", "Services" : [ { "Type" : "xtreemfs", "ServiceName" : "XtreemFS service", "Start" : 1, "VolumeStartup" : { "volumeName" : "data", "owner" : "www-data" } }, { "Type" : "mysql", "ServiceName" : "MySQL service", "Start" : 1, "Dump" : "https://online.conpaas.eu/owncloud/owncloud.sql", "Password" : "contrail123" }, { "Type" : "php", "ServiceName" : "PHP service", "Start" : 1, "Archive" : "https://online.conpaas.eu/owncloud/owncloud.tar.bz2", "StartupScript" : "https://online.conpaas.eu/owncloud/owncloud-startup.sh" } ]  }';

manifest['wordpress'] = '{ "Application" : "New Wordpress application", "Services" : [ { "Type" : "xtreemfs", "ServiceName" : "XtreemFS service", "Start" : 1, "VolumeStartup" : { "volumeName" : "data", "owner" : "www-data" } }, { "Type" : "mysql", "ServiceName" : "MySQL service", "Start" : 1, "Dump" : "https://online.conpaas.eu/wordpress/wordpress.sql", "Password" : "contrail123" }, { "Type" : "php", "ServiceName" : "PHP service", "Start" : 1, "Archive" : "https://online.conpaas.eu/wordpress/wordpress.tar.gz", "StartupScript" : "https://online.conpaas.eu/wordpress/wordpress.sh" } ]  }';

manifest['mediawiki'] = '{ "Application" : "New MediaWiki application", "Services" : [ { "Type" : "xtreemfs", "ServiceName" : "XtreemFS service", "Start" : 1, "VolumeStartup" : { "volumeName" : "data", "owner" : "www-data" } }, { "Type" : "mysql", "ServiceName" : "MySQL service", "Start" : 1, "Dump" : "https://online.conpaas.eu/mediawiki/mediawiki.sql", "Password" : "contrail123" }, { "Type" : "php", "ServiceName" : "PHP service", "Start" : 1, "Archive" : "https://online.conpaas.eu/mediawiki/mediawiki.tar.gz", "StartupScript" : "https://online.conpaas.eu/mediawiki/mediawiki.sh" } ]  }';


$(document).ready(function() {
	var selectedManifest = null;

	$('input:file').change(function() {
		if (selectedManifest) {
			selectedManifest.removeClass("selectedservice");
			selectedManifest.addClass("service");
		}
		$(this).addClass("selected");
		selectedManifest = null;
		$('input[name=type]').prop('checked', false);
	});

	$('.createpage .form .service').click(function () {
		if (selectedManifest === $(this)) {
			return;
		}
		if (selectedManifest) {
			selectedManifest.removeClass("selectedservice");
			selectedManifest.addClass("service");
		}
		selectedManifest = $(this);
		$(this).removeClass("service");
		$(this).addClass("selectedservice");
		$(this).find(':radio').prop('checked', true);
		$('input:file').val('');
		$('input:file').removeClass("selected");
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

		if (!selectedManifest) {
			alert("Please upload a file or select a ready-made application to continue.");
			return;
		}

		type = selectedManifest.find(':radio').val();
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
				return;
			}
			alert("The manifest was correctly uploaded. Now it can take a while to start everything.")
			window.location = 'services.php?aid=' + response.aid;
		});

	});
});
