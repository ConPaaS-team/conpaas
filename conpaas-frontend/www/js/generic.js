/*
 * Copyright (c) 2010-2014, Contrail consortium.
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

/**
 * @require conpaas.js, servicepage.js
 */
conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.GenericPage
     */
    this_module.GenericPage = conpaas.new_constructor(
    /* extends */conpaas.ui.ServicePage,
    /* constructor */function (server, service) {
        this.server = server;
        this.service = service;
        this.setupPoller_();
    },
    /* methods */{
    /**
     * @override conpaas.ui.ServicePage.freezeInput
     */
    freezeInput: function (freeze) {
        var linksSelectors = ['.activate', '.download', '.delete', '.dot'],
            buttons = ['refreshVolumeList', 'createVolume', 'deployApp'];
        conpaas.ui.ServicePage.prototype.freezeInput.call(this, freeze);
        this.freezeButtons(buttons, freeze);
        this.hideLinks(linksSelectors, freeze);
    },
    /**
     * @override conpaas.ui.ServicePage.attachHandlers
     */
    attachHandlers: function () {
        var that = this;
        conpaas.ui.ServicePage.prototype.attachHandlers.call(this);
        $('#fileForm').ajaxForm({
            dataType: 'json',
            success: function (response) {
                $('.additional .loading').toggleClass('invisible');
                $('#file').val('');
                // we need to perform error checking here, as we don't use
                // the server object that normally does that for us
                if (response.error) {
                    $('.additional .error').html(response.error);
                    $('.additional .error').show();
                    return;
                }
                $('.additional .positive').show();
                setTimeout(function () {
                    $('.additional .positive').fadeOut();
                }, 1000);
                that.reloadVersions();
            },
            error: function (response) {
                that.poller.stop();
                // show the error
                that.server.handleError({name: 'service error',
                    details: response.error});
           }
        });
        $('#fileForm input:file').change(function() {
            $('.additional .error').hide();
            $('.additional .loading').toggleClass('invisible');
            $('#fileForm').submit();
        });
        $('.versions .activate').click(that, that.onActivateVersion);
        $('.versions .delete').click(that, that.onDeleteVersion);
        $('.deployoption input[type=radio]').change(function() {
            $('.deployactions').toggleClass('invisible');
        });
        $('#createVolume').click(that, that.onCreateVolume);
        $('#refreshVolumeList').click(that, that.onRefreshVolumesList);
        $('#linkVolumes').click(this, this.onClickLinkVolumes);
        $('#deployApp').click(that, that.onDeployApp);
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

    deleteVolume: function (event, volumeName) {
		var page = event.data;
		if (volumeName.length == 0) {
			return;
		}
        if (!confirm('Are you sure you want to delete the volume ' + volumeName +
                '? All data contained within will be lost.')) {
            return;
        }
        page.freezeInput(true);
		//send the request
        page.server.req('ajax/genericRequest.php', {
            sid: page.service.sid,
            method: 'deleteVolume',
            volumeName: volumeName
        }, 'post', function (response) {
            // successful
            var message = "Command sent, waiting for the service to apply changes...";
            page.showStatus('#listVolumeStat', 'positive', message);
            page.pollState(function () {
                window.location.reload();
            });
        }, function (response) {
            // error
            page.showStatus('#listVolumeStat', 'error', response.details);
            page.freezeInput(false);
        });
    },

    makeDeleteHandler_: function (page, volumeName) {
        return function (event) {
            page.deleteVolume(event, volumeName);
        };
    },

    refreshVolumesList: function (showResult) {
        var page = this;
		//send the request
		page.freezeInput(true);
        page.server.req('ajax/genericRequest.php', {
            sid: page.service.sid,
            method: 'listVolumes'
        }, 'post', function (response) {
            // successful
            var volumes = response.result.volumes,
                listHTML = '';
            volumes.sort(function(a, b) {
                if (a.volumeName < b.volumeName)
                    return -1;
                if (a.volumeName > b.volumeName)
                    return 1;
                return 0;
            });
            for	(var i = 0; i < volumes.length; i++) {
                listHTML += '<tr class="service"><td class="wrapper'
                listHTML += (i == volumes.length - 1 ? ' last' : '') + '">';
                listHTML += '<div class="content generic-details">';
                listHTML += '<img src="images/volume.png">&nbsp;&nbsp;';
                listHTML += '<b>' + volumes[i].volumeName + '</b>';
                listHTML += ' (size <b>' + volumes[i].volumeSize + 'MB</b>,';
                listHTML += ' attached to <b>' + volumes[i].agentId + '</b>)';
                listHTML += '</div>';
                listHTML += '<div class="statistic"><div class="statcontent">';
                listHTML += '<img id="';
                listHTML += 'deleteVolume-' + volumes[i].volumeName;
                listHTML += '" src="images/remove.png">';
                listHTML += '</div></div>';
                listHTML += '<div class="clear"></div>';
                listHTML += '</td></tr>';
            }
            $('#volumesList').html(listHTML);
            for	(var i = 0; i < volumes.length; i++) {
                $('#deleteVolume-' + volumes[i].volumeName).click(page,
                        page.makeDeleteHandler_(page, volumes[i].volumeName));
            }
            if (!listHTML) {
				$('#noVolumesBox').show();
			} else {
                $('#noVolumesBox').hide();
            }
            if (showResult) {
                page.showStatus('#listVolumeStat', 'positive', 'Volume list refreshed');
            }
            page.freezeInput(false);
        }, function (response) {
            // error
            page.showStatus('#listVolumeStat', 'error', 'Volumes information not available');
            page.freezeInput(false);
        });
    },

    // handlers
    onActivateVersion: function (event) {
        var page = event.data,
            versionId = $(event.target).attr('name');
        $(event.target).parent().find('.loading').show();
        page.freezeInput(true);
        page.updateConfiguration({codeVersionId: versionId}, function () {
            page.displayInfo('updating all the instances...');
            page.pollState(function () {
                window.location.reload();
            });
        }, function () {
            $(event.target).parent().find('.loading').hide();
            page.freezeInput(false);
        });
    },

    onCreateVolume: function (event) {
		var page = event.data,
			volumeName = $('#volumeName').val(),
	        volumeSize = $('#volumeSize').val(),
	        agentId = $('#selectAgent').val();

		if (volumeName.length == 0) {
			page.showStatus('#VolumeStat', 'error', 'There is no volume name');
			$('#volumeName').focus();
			return;
		}
        if (!/^[1-9]\d*$/.test(volumeSize)) {
			page.showStatus('#VolumeStat', 'error', 'Volume size must be a positive integer');
			$('#volumeSize').val('');
			$('#volumeSize').focus();
			return;
        }
		if (selectAgent.length == 0) {
			page.showStatus('#VolumeStat', 'error', 'There is no agent selected');
			return;
		}
		//send the request
		page.freezeInput(true);
        page.server.req('ajax/genericRequest.php', {
            sid: page.service.sid,
            method: 'createVolume',
            volumeName: volumeName,
            volumeSize: volumeSize,
            agentId: agentId
        }, 'post', function (response) {
            // successful
            var message = "Command sent, waiting for the service to apply changes...";
            page.showStatus('#VolumeStat', 'positive', message);
            page.pollState(function () {
                window.location.reload();
            });
        }, function (response) {
            // error
            page.showStatus('#VolumeStat', 'error', response.details);
            page.freezeInput(false);
        });
    },

    onClickLinkVolumes: function (event) {
        $('#volumeName').focus();
        return false;
    },

    onRefreshVolumesList: function (event) {
        var page = event.data;
        page.refreshVolumesList(true);
    },

    onDeployApp: function (event) {
        var page = event.data;

        page.freezeInput(true);
        page.server.req('ajax/genericDeployApp.php', {
            sid: page.service.sid
        }, 'post', function (response) {
            // successful
            page.showStatus('#deployAppStat', 'positive', 'Script started successfully');
            page.freezeInput(false);
        }, function (response) {
            // error
            page.showStatus('#deployAppStat', 'error', 'The script was not started');
            page.freezeInput(false);
        });
    },

    onDeleteVersion: function (event) {
        var page = event.data,
            versionId = $(event.target).attr('name');
        if (!confirm('Are you sure you want to delete the version ' +
                versionId + '?')) {
            return;
        }
        $(event.target).parent().find('.loading').show();
        page.freezeInput(true);
        page.server.req('ajax/deleteCodeVersion.php', {
            sid: page.service.sid,
            codeVersionId: versionId
        }, 'post', function (response) {
            // successful
            page.displayInfo('updating all the instances...');
            page.pollState(function () {
                window.location.reload();
            });
        }, function (response) {
            // error
            $(event.target).parent().find('.loading').hide();
            page.freezeInput(false);
        });
    },

    /**
     * load the rendered HTML for the versions container
     */
    reloadVersions: function () {
        var that = this;
        this.server.reqHTML('ajax/render.php',
                {sid: this.service.sid, target: 'generic_versions'}, 'get',
                function (response) {
                    $('#versionsWrapper').html(response);
                    $('.versions .activate').click(that,
                            that.onActivateVersion);
                    $('.versions .delete').click(that,
                            that.onDeleteVersion);
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
        page = new conpaas.ui.GenericPage(server, service);
        page.attachHandlers();
        if (page.service.needsPolling()) {
            page.freezeInput(true);
            page.pollState(function () {
                window.location.reload();
            });
        }
        page.refreshVolumesList(false);
    }, function () {
        // error
        window.location = 'services.php';
    })
});
