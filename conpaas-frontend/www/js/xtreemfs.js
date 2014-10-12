
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
//        $('#downloadUserCert').click(this, this.onDownloadUserCert);
        $('#downloadClientCert').click(this, this.onDownloadClientCert);
        $('#refreshSelect').click(this, this.onRefreshSelect);
        $('#mountCommand').click(this, this.onClickCommand);
        $('#unmountCommand').click(this, this.onClickCommand);
        $('#linkVolumes').click(this, this.onClickLinkVolumes);
        $('#linkCert').click(this, this.onClickLinkCert);
        $('#mountPoint').focusout(this.refreshCommand);
        $('#certFilename').focusout(this.refreshCommand);
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
    refreshCommand: function () {
        var dirAddress = $('#dirAddress').text(),
            volume = $('#selectVolume').val(),
            mountPoint = $('#mountPoint').val(),
            certFilename = $('#certFilename').val();

            if (!dirAddress) {
				dirAddress = '<DIR-address>';
			}
            if (!volume) {
				volume = '<volume>';
			}
            if (!mountPoint) {
				mountPoint = '<mount-point>';
			}
            if (!certFilename) {
				certFilename = '<filename.p12>';
			}

            $('#mountCommand').val('mount.xtreemfs ' +
                dirAddress + '/' +
                volume + ' ' +
                mountPoint +
                ' --pkcs12-file-path ' +
                certFilename +
                ' --pkcs12-passphrase -');

            $('#unmountCommand').val('fusermount -u ' + mountPoint);
    },
    // handlers
    onCreateVolume: function (event) {
		var page = event.data,
			volumeName = $('#volume').val(),
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
            page.onRefreshSelect(event, volumeName);
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
            page.onRefreshSelect(event);
        }, function (response) {
            // error
            page.showStatus('#VolumeStat', 'error', 'Volume was not deleted');
            $('#deleteVolume').removeAttr('disabled');
        });
    },

    onDownloadUserCert: function (event) {
        var page = event.data,
            form = $('form#userCertForm')[0],
            passphrase = form.elements['passphrase'].value,
            passphrase2 = form.elements['passphrase2'].value,
            certFilename = form.elements['filename'].value;

        if ($('#user').val().length == 0) {
            page.showStatus('#userCertStat', 'error', 'The user field must not be empty');
            $('#user').focus();
            return false;
        }

        if (passphrase != passphrase2) {
            page.showStatus('#userCertStat', 'error', 'Retyped passphrase does not match');
            form.elements['passphrase'].value = '';
            form.elements['passphrase2'].value = '';
            form.elements['passphrase'].focus();
            return false;
        }

        form.submit();
        form.reset();

        $('#hintCert').hide();
        $('#certFilename').val(certFilename);
        page.refreshCommand();
    },

    onDownloadClientCert: function (event) {
        var page = event.data,
            form = $('form#clientCertForm')[0],
            passphrase = form.elements['passphrase'].value,
            passphrase2 = form.elements['passphrase2'].value,
            certFilename = form.elements['filename'].value;

        if (passphrase != passphrase2) {
            page.showStatus('#clientCertStat', 'error', 'Retyped passphrase does not match');
            form.elements['passphrase'].value = '';
            form.elements['passphrase2'].value = '';
            form.elements['passphrase'].focus();
            return false;
        }

        form.submit();
        form.reset();

        $('#hintCert').hide();
        $('#certFilename').val(certFilename);
        page.refreshCommand();
    },

    onClickCommand: function (event) {
        var page = event.data;

        page.refreshCommand();
        $(this).focus().select();
    },

    onClickLinkVolumes: function (event) {
        $('#volume').focus();
    },

    onClickLinkCert: function (event) {
        $('form#clientCertForm')[0].elements['passphrase'].focus();
    },

    onRefreshSelect: function (event, selectedVolume) {
        var page = event.data,
            standardErrorText = 'Volumes information not available';

        $('#selectVolume').attr('disabled','disabled');
        $('#refreshSelect').attr('disabled','disabled');
        $('#hintVolume').hide();
        page.server.reqHTML('viewVolumes.php', {
            sid: page.service.sid
        }, 'get', function (response) {
            // successful
            $('#selectVolume').removeAttr('disabled');
            $('#refreshSelect').removeAttr('disabled');
            $('.selectHint, .msgbox').hide();
            if (response.indexOf(standardErrorText) > -1) {
                page.showStatus('#selectVolumeStat', 'error', standardErrorText);
                $('#selectVolume').html('');
                page.refreshCommand();
                return;
            }
            var re = /\n\t(.+)\t->\t/g,
                m, options = '',
                oldVal = selectedVolume || $('#selectVolume').val();
            while (m = re.exec(response)) {
                options += '<option value="' + m[1] + '"';
                if (m[1] == oldVal) {
                    options += ' selected="selected"';
                }
                options += '>' + m[1] + '</option>';
            }
            $('#selectVolume').html(options);
            page.refreshCommand();
            if (!options) {
				$('#hintVolume').show();
			}
        }, function (response) {
            // error
            $('#selectVolume').removeAttr('disabled');
            $('#refreshSelect').removeAttr('disabled');
            page.showStatus('#selectVolumeStat', 'error', response);
            $('#selectVolume').html('');
            page.refreshCommand();
        });
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
        $('#refreshSelect').click();
    }, function () {
        // error
        window.location = 'services.php';
    })
});
