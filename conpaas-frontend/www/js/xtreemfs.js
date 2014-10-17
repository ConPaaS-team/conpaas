
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
        var that = this;
        conpaas.ui.ServicePage.prototype.attachHandlers.call(this);
        $('#createVolume').click(this, this.onCreateVolume);
        $('#deleteVolume').click(this, this.onDeleteVolume);
//        $('#downloadUserCert').click(this, this.onDownloadUserCert);
        $('#downloadClientCert').click(this, this.onDownloadClientCert);
        $('#refreshSelect').click(this, this.onRefreshSelect);
        $('#refreshVolumeList').click(this, this.onRefreshVolumesList);
        $('#mountCommand').click(this, this.onClickCommand);
        $('#unmountCommand').click(this, this.onClickCommand);
        $('#linkVolumes').click(this, this.onClickLinkVolumes);
        $('#linkVolumes2').click(this, this.onClickLinkVolumes);
        $('#linkCert').click(this, this.onClickLinkCert);
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
    deleteVolume: function (event, volumeName) {
		var page = event.data;
		if (volumeName.length == 0) {
			return;
		}
        if (!confirm('Are you sure you want to delete the volume ' + volumeName +
                '? All data contained within will be lost.')) {
            return;
        }
		//send the request
        page.server.req('ajax/deleteVolume.php', {
            sid: page.service.sid,
            volumeName: volumeName
        }, 'post', function (response) {
            // successful
            page.showStatus('#listVolumeStat', 'positive', 'The Volume was deleted successfully');
            $('.selectHint, .msgbox').hide();
            page.onRefreshSelect(event);
        }, function (response) {
            // error
            page.showStatus('#listVolumeStat', 'error', 'Volume was not deleted');
        });
    },
    makeDeleteHandler_: function (page, volumeName) {
        return function (event) {
            page.deleteVolume(event, volumeName);
        };
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

    onRefreshSelect: function (event, selectedVolume, showResult) {
        var page = event.data,
            standardErrorText = 'Volumes information not available';

        $('#selectVolume').attr('disabled','disabled');
        $('#refreshSelect').attr('disabled','disabled');
        $('#refreshVolumeList').attr('disabled','disabled');
        $('#hintVolume').hide();
        page.server.reqHTML('viewVolumes.php', {
            sid: page.service.sid
        }, 'get', function (response) {
            // successful
            $('#selectVolume').removeAttr('disabled');
            $('#refreshSelect').removeAttr('disabled');
            $('#refreshVolumeList').removeAttr('disabled');
            $('.selectHint, .msgbox').hide();
            if (response.indexOf(standardErrorText) > -1) {
                page.showStatus('#selectVolumeStat', 'error', standardErrorText);
                page.showStatus('#listVolumeStat', 'error', standardErrorText);
                $('#selectVolume').html('');
                page.refreshCommand();
                return;
            }
            var re = /\n\t(.+)\t->\t/g, m, volumeName,
                optionsHTML = '', listHTML = '',
                volumeNames = Array(),
                oldVal = selectedVolume || $('#selectVolume').val();
            while (m = re.exec(response)) {
                volumeNames.push(m[1]);
            }
            volumeNames.sort();
            for	(var i = 0; i < volumeNames.length; i++) {
                optionsHTML += '<option value="' + volumeNames[i] + '"';
                if (volumeNames[i] == oldVal) {
                    optionsHTML += ' selected="selected"';
                }
                optionsHTML += '>' + volumeNames[i] + '</option>';

                listHTML += '<tr class="service"><td class="wrapper'
                listHTML += (i == volumeNames.length - 1 ? ' last' : '') + '">';
                listHTML += '<div class="content xtreemfs-details">';
                listHTML += '<img src="images/volume.png">&nbsp;&nbsp;';
                listHTML += volumeNames[i];
                listHTML += '</div>';
                listHTML += '<div class="statistic"><div class="statcontent">';
                listHTML += '<img id="';
                listHTML += 'deleteVolume-' + volumeNames[i];
                listHTML += '" src="images/remove.png">';
                listHTML += '</div></div>';
                listHTML += '<div class="clear"></div>';
                listHTML += '</td></tr>';
            }
            $('#selectVolume').html(optionsHTML);
            $('#volumesList').html(listHTML);
            for	(var i = 0; i < volumeNames.length; i++) {
                $('#deleteVolume-' + volumeNames[i]).click(page,
                        page.makeDeleteHandler_(page, volumeNames[i]));
            }
            if (!optionsHTML) {
				$('#hintVolume').show();
				$('#noVolumesBox').show();
			} else {
                $('#noVolumesBox').hide();
            }
            page.refreshCommand();
            if (showResult) {
                page.showStatus('#listVolumeStat', 'positive', 'Volume list refreshed');
            }
            return true;
        }, function (response) {
            // error
            $('#selectVolume').removeAttr('disabled');
            $('#refreshSelect').removeAttr('disabled');
            $('#refreshVolumeList').removeAttr('disabled');
            page.showStatus('#selectVolumeStat', 'error', response);
            page.showStatus('#listVolumeStat', 'error', response);
            $('#selectVolume').html('');
            $('#noVolumesBox').hide();
            page.refreshCommand();
        });
    },

    onRefreshVolumesList: function (event, selectedVolume) {
        var page = event.data;
        page.onRefreshSelect(event, selectedVolume, true);
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
        $('#refreshSelect').click();
    }, function () {
        // error
        window.location = 'services.php';
    })
});
