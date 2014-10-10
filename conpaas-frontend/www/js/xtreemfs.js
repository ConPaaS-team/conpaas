
/* Copyright (C) 2010-2013 by Contrail Consortium. */



conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.MysqlPage
     */
    this_module.XtreemFSPage = conpaas.new_constructor(
    /* extends */conpaas.ui.ServicePage,
    /* constructor */function (server, service) {
        this.server = server;
        this.service = service;
        this.setupPoller_();
    },
    /* methods */{
    /**
     * @override conpaas.ui.ServicePage.attachHandlers
     */
    attachHandlers: function () {
        var that = this;
        conpaas.ui.ServicePage.prototype.attachHandlers.call(this);
        $('#createVolume').click(this, this.onCreateVolume);
        $('#deleteVolume').click(this, this.onDeleteVolume);
        $('#downloadUserCert').click(this, this.onDownloadUserCert);
        $('#downloadClientCert').click(this, this.onDownloadClientCert);
    },
    showStatus: function (statusId, type, message) {
        var otherType = (type === 'positive') ? 'error' : 'positive';
        $(statusId).removeClass(otherType).addClass(type)
            .html(message)
            .show();
        setTimeout(function () {
            $(statusId).fadeOut();
        }, 3000);
    },
    // handlers
    onCreateVolume: function (event) {
		var page = event.data,
			volumeName = $('#volume').val();
	        owner = $('#owner').val();	
		if(volumeName.length == 0){
			page.showStatus('#VolumeStat', 'error','There is no volume name');	
			return;
		}

		if(owner.length == 0){
			page.showStatus('#VolumeStat', 'error','There is no owner');	
			return;
		}
		//send the request
		$('#createVolume').attr('disabled','disabled');
        page.server.req('ajax/createVolume.php', {
            sid: page.service.sid,
            volumeName: volumeName,
            owner: owner
        }, 'post', function (response) {
            // successful
            page.showStatus('#VolumeStat', 'positive', 'The Volume was created successfully');
            $('#createVolume').removeAttr('disabled');
            $('#volume').val('');
            $('#owner').val('');
            $('.selectHint, .msgbox').hide();
        }, function (response) {
            // error
            page.showStatus('#VolumeStat', 'error', 'Volume was not created');
            $('#createVolume').removeAttr('disabled');
        });
    },

    onDeleteVolume: function (event) {
		var page = event.data,
			volumeName = $('#volume').val();
		
		if(volumeName.length == 0){
			page.showStatus('#VolumeStat', 'error','There is no volume name');	
			return;
		}
		//send the request
		$('#deleteVolume').attr('disabled','disabled');
        page.server.req('ajax/deleteVolume.php', {
            sid: page.service.sid,
            volumeName: volumeName
        }, 'post', function (response) {
            // successful
            page.showStatus('#VolumeStat', 'positive', 'The Volume was deleted successfully');
            $('#deleteVolume').removeAttr('disabled');
            $('#volume').val('');
            $('#owner').val('');
            $('.selectHint, .msgbox').hide();
        }, function (response) {
            // error
            page.showStatus('#VolumeStat', 'error', 'Volume was not deleted');
            $('#deleteVolume').removeAttr('disabled');
        });
    },

    onDownloadUserCert: function (event) {
        var page = event.data,
            form = $('form#userCertForm')[0];

        if ($('#user').val().length == 0) {
            page.showStatus('#userCertStat', 'error', 'The user field must not be empty');
            return false;
        }

        passphrase = form.elements['passphrase'].value;
        passphrase2 = form.elements['passphrase2'].value;
        if (passphrase != passphrase2) {
            page.showStatus('#userCertStat', 'error', 'Retyped passphrase does not match');
            return false;
        }

        form.submit();
        form.reset();
    },

    onDownloadClientCert: function (event) {
        var page = event.data,
            form = $('form#clientCertForm')[0];

        passphrase = form.elements['passphrase'].value;
        passphrase2 = form.elements['passphrase2'].value;
        if (passphrase != passphrase2) {
            page.showStatus('#clientCertStat', 'error', 'Retyped passphrase does not match');
            return false;
        }

        form.submit();
        form.reset();
    }

    });

    return this_module;
}(conpaas.ui || {}));

$(document).ready(function () {
    var service,
        page,
        sid = GET_PARAMS['sid'],
        server = new conpaas.http.Xhr();
    server.req('ajax/getService.php', {sid: sid}, 'get', function (data) {
        service = new conpaas.model.Service(data.sid, data.state,
                data.instanceRoles, data.reachable);
        page = new conpaas.ui.XtreemFSPage(server, service);
        page.attachHandlers();
        if (page.service.needsPolling()) {
            page.freezeInput(true);
            page.pollState(function () {
                window.location.reload();
            });
        }
    }, function () {
        // error
        window.location = 'services.php';
    })
});
