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
 * @require conpaas.js, service.js
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
        this.scriptStatusTimeoutId_ = null;
    },

    /* methods */{
    /**
     * @override conpaas.ui.ServicePage.freezeInput
     */
    freezeInput: function (freeze) {
        var links = ['.activate', '.download', '.delete', '.dot'],
            buttons = ['.create-volume-button'],
            commandButtons = [ '#runApp', '#interruptApp', '#cleanupApp'];
        conpaas.ui.ServicePage.prototype.freezeInput.call(this, freeze);
        this.freezeButtons(buttons, freeze);
        this.hideLinks(links, freeze);
        if (freeze) {
            this.freezeButtons(commandButtons, freeze);
            this.stopScriptStatePolling();
        } else {
            this.reloadInstances();
        }
    },

    /**
     * @override conpaas.ui.ServicePage.attachHandlers
     */
    attachHandlers: function () {
        var page = this;
        conpaas.ui.ServicePage.prototype.attachHandlers.call(this);
        $('#fileForm').ajaxForm({
            dataType: 'json',
            success: function (response) {
                $('.additional .loading').toggleClass('invisible');
                $('#file').val('');
                // we need to perform error checking here, as we don't use
                // the server object that normally does that for us
                if (response.error) {
                    page.showStatus('#uploadFileStat', 'error', response.error);
                    return;
                }
                page.showStatus('#uploadFileStat', 'positive', "Submitted successfully");
                page.reloadVersions();
            },
            error: function (response) {
                page.poller.stop();
                // show the error
                page.server.handleError({name: 'service error',
                    details: response.error});
           }
        });
        $('#fileForm input:file').change(function() {
            page.freezeInput(true);
            $('.additional .loading').toggleClass('invisible');
            $('#fileForm').submit();
            page.freezeInput(false);
        });
        $('#submitPubKey').click(page, page.onSubmitPubKey);
        $('.deployoption input[type=radio]').change(function() {
            $('#uploadFileStat, #uploadKeyStat').hide();
            $('.deployactions').toggleClass('invisible');
        });
        $('.versions .activate').click(page, page.onActivateVersion);
        $('.versions .delete').click(page, page.onDeleteVersion);
        $('.volumes .delete').click(page, page.onDeleteVolume);
        $('.create-volume-link').click(page, page.onClickAddVolumes);
        $('.create-volume-button').click(page, page.onCreateVolume);
        $('#runApp, #interruptApp, #cleanupApp').click(page,
                                                    page.onExecuteScript);

        page.defaultRunTooltip = $('#runApp').attr('title');
        page.defaultInterruptTooltip = $('#interruptApp').attr('title');
        page.defaultCleanupTooltip = $('#cleanupApp').attr('title');
        page.updateCommandButtons();
        if (page.areScriptsRunning()) {
            page.startScriptStatePolling();
        }
    },

    // handlers
    onActivateVersion: function (event) {
        var page = event.data,
            versionId = $(event.target).attr('name');

        if (page.areScriptsRunning()) {
            alert("Scripts are still running inside at " +
                                "least one agent. Please wait for them to " +
                                "finish execution or call 'interrupt' first.");
            return;
        }
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
            agentId = $(event.target).attr('name'),
            volumeName = $('#' + agentId + '-volumeName').val(),
            volumeSize = $('#' + agentId + '-volumeSize').val();

		if (volumeName.length == 0) {
			page.showStatus('#' + agentId + '-VolumeStat', 'error',
						'There is no volume name');
			$('#' + agentId + '-volumeName').focus();
			return;
		}
        if (!/^[A-za-z0-9-_]+$/.test(volumeName)) {
			page.showStatus('#' + agentId + '-VolumeStat', 'error',
						'Volume name contains invalid characters');
			$('#' + agentId + '-volumeName').val('');
			$('#' + agentId + '-volumeName').focus();
			return;
        }
        if (!/^[1-9]\d*$/.test(volumeSize)) {
			page.showStatus('#' + agentId + '-VolumeStat', 'error',
						'Volume size must be a positive integer');
			$('#' + agentId + '-volumeSize').val('');
			$('#' + agentId + '-volumeSize').focus();
			return;
        }
        if (page.areScriptsRunning()) {
            alert("Scripts are still running inside at " +
                                "least one agent. Please wait for them to " +
                                "finish execution or call 'interrupt' first.");
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
            page.showStatus('#' + agentId + '-VolumeStat', 'positive', message);
            page.pollState(function () {
                window.location.reload();
            });
        }, function (response) {
            // error
            page.showStatus('#' + agentId + '-VolumeStat', 'error', response.details);
            page.freezeInput(false);
        });
    },

    onDeleteVolume: function (event) {
		var page = event.data,
            volumeName = $(event.target).attr('name'),
            agentId = $(event.target).parent().attr('name');

        if (page.areScriptsRunning()) {
            alert("Scripts are still running inside at " +
                                "least one agent. Please wait for them to " +
                                "finish execution or call 'interrupt' first.");
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
            page.showStatus('#' + agentId + '-VolumeStat', 'positive', message);
            page.pollState(function () {
                window.location.reload();
            });
        }, function (response) {
            // error
            page.showStatus('#' + agentId + '-VolumeStat', 'error', response.details);
            page.freezeInput(false);
        });
    },

    onClickAddVolumes: function (event) {
        var page = event.data,
            agentId = $(event.target).attr('name');

            $('.generic.create[name=' + agentId + ']').toggle(400);

            if ($(event.target).text().charAt(0) == '+') {
                $(event.target).text('— add volume');
                $(event.target).attr('title', 'hide volume creation form');
                $('#' + agentId + '-volumeName').focus();
            } else {
                $(event.target).text('+ add volume');
                $(event.target).attr('title', 'show volume creation form');
                $('#' + agentId + '-volumeName').val('');
                $('#' + agentId + '-volumeSize').val('');
                $('#' + agentId + '-VolumeStat').fadeOut();
            }
    },

    onExecuteScript: function (event) {
        var page = event.data,
            command = $(event.target).attr('name'),
            parameters = $('#scriptParameters').val();

        page.freezeInput(true);
        page.server.req('ajax/genericRequest.php', {
            sid: page.service.sid,
            method: 'executeScript',
            command: command,
            parameters: parameters
        }, 'post', function (response) {
            // successful
            if (command == 'interrupt' && page.isScriptRunning(command + '.sh')) {
                page.showStatus('#appLifecycleStat', 'positive', "Script '" + command +
                                ".sh' is already running, killing all the processes.");
            } else {
                page.showStatus('#appLifecycleStat', 'positive',
                        "Script '" + command + ".sh' started successfully");
            }
            page.freezeInput(false);
        }, function (response) {
            // error
            page.showStatus('#appLifecycleStat', 'error', 'The script was not started');
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

    onSubmitPubKey: function (event) {
        var page = event.data;
        var pubkey = $('#pubkey').val();

        if (!pubkey.match(/^ssh-(rsa|dss)/)) {
            page.showStatus('#uploadKeyStat', 'error',
                    "Key is invalid. It must begin with 'ssh-rsa' or 'ssh-dss'.");
            $('#pubkey').val('');
            $('#pubkey').focus();
            return false;
        }

        page.freezeInput(true);
        $('.additional .loading').toggleClass('invisible');

        page.server.req('ajax/uploadSshPubKey.php', {
            sid: page.service.sid,
            sshkey: pubkey
        }, 'post', function (response) {
            // successful
            page.showStatus('#uploadKeyStat', 'positive', "Submitted successfully");
            $('.additional .loading').toggleClass('invisible');
            page.freezeInput(false);
        }, function (response) {
            // error
            page.showStatus('#uploadKeyStat', 'error', response.error);
            $('.additional .loading').toggleClass('invisible');
            page.freezeInput(false);
        });
    },

    /**
     * load the rendered HTML for the versions container
     */
    reloadVersions: function () {
        var page = this;
        page.server.reqHTML('ajax/render.php', {
            sid: this.service.sid,
            target: 'versions'
        }, 'get', function (response) {
            $('#versionsWrapper').html(response);
            $('.versions .activate').click(page,
                    page.onActivateVersion);
            $('.versions .delete').click(page,
                    page.onDeleteVersion);
        });
    },

    /**
     * load the rendered HTML for the instances container
     */
    reloadInstances: function () {
        var page = this;
        $.ajax({
            url: 'ajax/render.php',
            dataType: 'json',
            data: {
                sid: this.service.sid,
                target: 'generic_script_status'
            },
            success: function (response) {
                if (response.error) {
                    return;
                }
                for (var agentId in response) {
                    $('#' + agentId + '-scriptStatusWrapper').html(response[agentId]);
                }
                page.updateCommandButtons();
                if (page.areScriptsRunning()) {
                    page.startScriptStatePolling();
                } else {
                    page.stopScriptStatePolling();
                }
            }
        });
    },

    /**
     * check if there are scripts currently RUNNING inside any
     * of the agents
     */
    areScriptsRunning: function () {
        var instancesText = $('#instancesWrapper').text();
        return instancesText.indexOf("RUNNING") != -1;
    },

    /**
     * check if a specific script is RUNNING inside any of the
     * agents
     */
    isScriptRunning: function (script) {
        var instancesText = $('#instancesWrapper').text(),
            regExp = new RegExp(script + '\\s*RUNNING');
        return instancesText.search(regExp) != -1;
    },

    /**
     * update execute command buttons according to the state of the scripts
     */
    updateCommandButtons: function () {
        var page = this,
            killTooltip = "pressing this button will kill all the running processes",
            runningTooltip = "scripts are running inside at least one agent, " +
                    "wait for them to finish execution or call 'interrupt' first",
            notRunningTooltip = "no scripts are currently running inside agents, " +
                    "nothing to interrupt";

        if (page.areScriptsRunning()) {
            // disable the 'run' button
            $('#runApp').attr('disabled', 'disabled');
            $('#runApp').attr('title', runningTooltip);

            // enable the 'interrupt' button and set its label to 'interrupt'
            // or 'kill'
            $('#interruptApp').removeAttr('disabled');
            if (page.isScriptRunning('interrupt.sh')) {
                $("#interruptApp").attr('value', 'kill');
                $('#interruptApp').attr('title', killTooltip);
            } else {
                $("#interruptApp").attr('value', 'interrupt');
                $('#interruptApp').attr('title', page.defaultInterruptTooltip);
            }

            // disable the 'cleanup' button
            $('#cleanupApp').attr('disabled', 'disabled');
            $('#cleanupApp').attr('title', runningTooltip);
        } else {
            // enable the 'run' button
            $('#runApp').removeAttr('disabled');
            $('#runApp').attr('title', page.defaultRunTooltip);

            // disable the 'interrupt' button and set its label to 'interrupt'
            $("#interruptApp").attr('value', 'interrupt');
            $('#interruptApp').attr('disabled', 'disabled');
            $('#interruptApp').attr('title', notRunningTooltip);

            // enable the 'cleanup' button
            $('#cleanupApp').removeAttr('disabled');
            $('#cleanupApp').attr('title', page.defaultCleanupTooltip);
        }
    },

    /**
     * start polling the script states
     */
    startScriptStatePolling: function () {
        var page = this;
        // animate the 'RUNNING' icon
        $('.running').fadeOut(500).fadeIn(500);
        page.scriptStatusTimeoutId_ = setTimeout(function () {
            page.reloadInstances();
        }, 1000);
    },

    /**
     * stop polling the script states
     */
    stopScriptStatePolling: function () {
        var page = this;
        if (page.scriptStatusTimeoutId_ == null) {
            // polling already stopped
            return;
        }
        clearTimeout(page.scriptStatusTimeoutId_);
        page.scriptStatusTimeoutId_ = null;
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
    }, function () {
        // error
        window.location = 'application.php';
    })
});
