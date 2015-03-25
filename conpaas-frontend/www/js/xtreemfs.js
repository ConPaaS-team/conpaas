
/* Copyright (C) 2010-2013 by Contrail Consortium. */



conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.XtreemFSPage
     */
    this_module.XtreemFSPage = conpaas.new_constructor(
    /* extends */conpaas.ui.ServicePage,
    /* constructor */function (server, service) {
        this.server = server;
        this.service = service;
        this.setupPoller_();
    },

    /* methods */ {
    /**
     * @override conpaas.ui.ServicePage.freezeInput
     */
    freezeInput: function (freeze) {
        var linksSelectors = ['.delete'],
            buttons = ['downloadClientCert', // 'downloadUserCert',
                       'refreshVolumeList', 'createVolume', 'refreshSelect',
                       'selectVolume'];
        conpaas.ui.ServicePage.prototype.freezeInput.call(this, freeze);
        this.freezeButtons(buttons, freeze);
        this.hideLinks(linksSelectors, freeze);
    },

    /**
     * @override conpaas.ui.ServicePage.showStatus
     */
    showStatus: function (statusSelector, type, message) {
        var otherType = (type === 'positive') ? 'error' : 'positive';
        $(statusSelector).removeClass(otherType).addClass(type)
            .html(message)
            .show();
        if (statusSelector == "#selectVolumeStat") {
            $('#hintVolume').hide();
        }
        setTimeout(function () {
            if (statusSelector == "#selectVolumeStat") {
                $(statusSelector).hide();
                $('#hintVolume').show();
            } else {
                $(statusSelector).fadeOut();
            }
        }, 3000);
    },

    /**
     * @override conpaas.ui.ServicePage.getStopWarningText
     */
    getStopWarningText: function () {
        return 'All data stored in the XtreemFS service ' +
               'will be lost. Are you sure you want to stop the service?';
    },

    /**
     * @override conpaas.ui.ServicePage.attachHandlers
     */
    attachHandlers: function () {
        conpaas.ui.ServicePage.prototype.attachHandlers.call(this);

        $('#downloadClientCert').click(this, this.onDownloadClientCert);
//        $('#downloadUserCert').click(this, this.onDownloadUserCert);
        $('#createVolume').click(this, this.onCreateVolume);
        $('.volumes .delete').click(this, this.onDeleteVolume);
        $('.linkVolumes').click(this, this.onClickLinkVolumes);
        $('#linkCert').click(this, this.onClickLinkCert);
        $('#refreshVolumeList').click(this, this.onRefreshVolumesList);
        $('#selectVolume').click(this.refreshCommand);
        $('#refreshSelect').click(this, this.onRefreshSelect);
        $('#mountCommand').click(this, this.onClickCommand);
        $('#unmountCommand').click(this, this.onClickCommand);

        $('#mountPoint').focusout(this.refreshCommand);
        $('#certFilename').focusout(this.refreshCommand);

        $('#volume').keypress('createVolume', this.onEnterPressed);
        $('#owner').keypress('createVolume', this.onEnterPressed);
        $('#clientCertForm input[name="passphrase"]').keypress(
                'downloadClientCert', this.onEnterPressed);
        $('#clientCertForm input[name="passphrase2"]').keypress(
                'downloadClientCert', this.onEnterPressed);
        $('#clientCertForm input[name="filename"]').keypress(
                'downloadClientCert', this.onEnterPressed);
/*        $('#userCertForm input[name="passphrase"]').keypress(
                'downloadUserCert', this.onEnterPressed);
        $('#userCertForm input[name="passphrase2"]').keypress(
                'downloadUserCert', this.onEnterPressed);
        $('#userCertForm input[name="filename"]').keypress(
                'downloadUserCert', this.onEnterPressed); */
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

    refreshVolumes: function (statusSelector, selectedVolume) {
        var page = this;

        if (!selectedVolume) {
            selectedVolume = $('#selectVolume').val();
        }

        //send the request
        page.freezeInput(true);
        page.server.req('ajax/render.php', {
            sid: page.service.sid,
            target: 'xtreemfs_volumes'},
        'get', function (response) {
            $('#volumeListWrapper').html(response.volumeList);
            $('#volumeSelectorWrapper').html(response.volumeSelector);
            $('.linkVolumes').click(page, page.onClickLinkVolumes);
            $('.volumes .delete').click(page, page.onDeleteVolume);
            $('#selectVolume').click(this.refreshCommand);
            $('#refreshSelect').click(page, page.onRefreshSelect);
            if (statusSelector) {
                page.showStatus(statusSelector, 'positive', 'Volume list refreshed');
            }
            if (selectedVolume) {
                $('#selectVolume option[value="' + selectedVolume + '"]')
                        .attr('selected', 'selected');
            }
            page.refreshCommand();
            page.freezeInput(false);
         }, function (response) {
            // error
            if (statusSelector) {
                page.showStatus(statusSelector, 'error', 'Volumes information not available');
            }
            page.freezeInput(false);
        });
    },

    // handlers
    onCreateVolume: function (event) {
		var page = event.data,
			volumeName = $('#volume').val(),
	        owner = $('#owner').val();

		if (volumeName.length == 0) {
			page.showStatus('#VolumeStat', 'error', 'There is no volume name');
			$('#volume').focus();
			return;
		}
		if (owner.length == 0) {
			page.showStatus('#VolumeStat', 'error', 'There is no owner');
			$('#owner').focus();
			return;
		}

		//send the request
		page.freezeInput(true);
        page.server.req('ajax/createVolume.php', {
            sid: page.service.sid,
            volumeName: volumeName,
            owner: owner
        }, 'post', function (response) {
            // successful
            page.showStatus('#VolumeStat', 'positive', 'The volume was created successfully');
            $('#volume').val('');
            $('#owner').val('');
            $('.selectHint, .msgbox').hide();
            page.refreshVolumes(null, volumeName);
        }, function (response) {
            // error
            page.showStatus('#VolumeStat', 'error', response.details);
            page.freezeInput(false);
        });
    },

    onDeleteVolume: function (event) {
		var page = event.data,
			volumeName = $(event.target).attr('name');

		if (volumeName.length == 0) {
			return;
		}
        if (!confirm('Are you sure you want to delete the volume ' + volumeName +
                '? All data contained within will be lost.')) {
            return;
        }

		//send the request
        page.freezeInput(true);
        page.server.req('ajax/deleteVolume.php', {
            sid: page.service.sid,
            volumeName: volumeName
        }, 'post', function (response) {
            // successful
            page.showStatus('#listVolumeStat', 'positive', 'The volume was deleted successfully');
            $('.selectHint, .msgbox').hide();
            page.refreshVolumes();
        }, function (response) {
            // error
            page.showStatus('#listVolumeStat', 'error', response.details);
            page.freezeInput(false);
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
        if (passphrase.length == 0) {
            page.showStatus('#userCertStat', 'error', 'The passphrase must not be empty');
            form.elements['passphrase'].focus();
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

        if (passphrase.length == 0) {
            page.showStatus('#clientCertStat', 'error', 'The passphrase must not be empty');
            form.elements['passphrase'].focus();
            return false;
        }
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
        return false;
    },

    onClickLinkCert: function (event) {
        $('form#clientCertForm')[0].elements['passphrase'].focus();
        return false;
    },

    onRefreshVolumesList: function (event) {
        var page = event.data;
        page.refreshVolumes("#listVolumeStat");
    },

    onRefreshSelect: function (event) {
        var page = event.data;
        page.refreshVolumes("#selectVolumeStat");
    },

    onEnterPressed: function (event) {
        var buttonToBePressed = event.data;
        if (event.keyCode == 13) {
            $('#' + buttonToBePressed).click();
        }
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
