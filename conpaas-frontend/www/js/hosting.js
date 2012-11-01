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

/**
 * @require conpaas.js, servicepage.js
 */
conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.HostingPage
     */
    this_module.HostingPage = conpaas.new_constructor(
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
        var linksSelector = '.versions .activate',
            buttons = ['cds_subscribe', 'cds_unsubscribe'];
        conpaas.ui.ServicePage.prototype.freezeInput.call(this, freeze);
        this.freezeButtons(buttons, freeze);
        if (freeze) {
            $(linksSelector).hide();
        } else {
            $(linksSelector).show();
        }
    },
    /**
     * @override conpaas.ui.ServicePage.attachHandlers
     */
    attachHandlers: function () {
        var that = this;
        conpaas.ui.ServicePage.prototype.attachHandlers.call(this);
        // this is the goofy ajax file submit form provided by a jQuery plugin
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
        $('.deployoption input[type=radio]').change(function() {
            $('.deployactions').toggleClass('invisible');
        });
        // configuration handlers
        $('#conf-maxexec, #conf-memlim, #conf-uploadmaxsize, #conf-postmaxsize').change(function() {
            $('#saveconf').removeAttr('disabled');
        });
        $('#saveconf').click(that, that.onSaveConfig);
        $('#cds_subscribe').click(that, that.onCdsSubscribe);
        $('#cds_unsubscribe').click(that, that.onCdsUnsubscribe);
        $('#submitPubKey').click(that, that.onSubmitPubKey);        
        $('#submitStartupScript').click(that, that.onSubmitStartupScript);        
        $('#mountVolume').click(this, this.onMountVolume);
        $('#umountVolume').click(this, this.onUmountVolume);
    },
    showCreateVolStatus: function (type, message) {
        var otherType = (type === 'positive') ? 'error' : 'positive';
        $('#VolumeStat').removeClass(otherType).addClass(type)
            .html(message)
            .show();
        setTimeout(function () {
            $('#VolumeStat').fadeOut();
        }, 3000);
    },
    // handlers
    onMountVolume: function (event){
        var page = event.data,
            volume = $('#volume').val(),
            path = $('#path').val();

		if(volume.length == 0){
			page.showCreateVolStatus('error','There is no volume name');	
			return;
		}

		if(path.length == 0){
			page.showCreateVolStatus('error','There is no path');	
			return;
		}
		//send the request
		$('#createVolume').attr('disabled','disabled');
        page.server.req('ajax/mountVolume.php', {
            sid: page.service.sid,
            volume: volume,
            path :path
        }, 'post', function (response) {
            // successful
            page.showCreateVolStatus('positive', 'The Volume was successfully mounted');
            $('#mountVolume').removeAttr('disabled');
            $('#volume').val('');
            $('.selectHint, .msgbox').hide();
        }, function (response) {
            // error
            page.showCreateVolStatus('error', 'Volume was not mounted');
            $('#mountVolume').removeAttr('disabled');
        });
    },
    onUmountVolume: function (event){
        var page = event.data,
            path = $('#path').val();


		if(path.length == 0){
			page.showCreateVolStatus('error','There is no path');	
			return;
		}
		//send the request
		$('#umountVolume').attr('disabled','disabled');
        page.server.req('ajax/umountVolume.php', {
            sid: page.service.sid,
            path :path
        }, 'post', function (response) {
            // successful
            page.showCreateVolStatus('positive', 'The Volume was successfully unmounted');
            $('#umountVolume').removeAttr('disabled');
            $('#volume').val('');
            $('.selectHint, .msgbox').hide();
        }, function (response) {
            // error
            page.showCreateVolStatus('error', 'Volume was not unmounted');
            $('#umountVolume').removeAttr('disabled');
        });
    },
    onActivateVersion: function (event) {
        var page = event.data,
            versionId = $(event.target).attr('name');
        $('.versions .activate').hide();
        $(event.target).parent().find('.loading').show();
        page.freezeInput(true);
        page.updateConfiguration({codeVersionId: versionId}, function () {
            page.displayInfo('updating all the instances...');
            page.pollState(function () {
                window.location.reload();
            });
        }, function () {
            page.freezeInput(false);
        });
    },
    uploadTextArea: function (page, url, params, additionalClass) {
        page.freezeInput(true);
        $(additionalClass + ' .loading').toggleClass('invisible');

        page.server.req(url, params,
                'post', function (response) {
                    page.freezeInput(false);
                    if (response.error) {
                        $(additionalClass + ' .error').html(response.error);
                        $(additionalClass + ' .error').show();
                        return false;
                    }

                    $(additionalClass + ' .loading').toggleClass('invisible');
                    $(additionalClass + ' .positive').show();

                    setTimeout(function () {
                        $(additionalClass + ' .positive').fadeOut();
                    }, 1000);

                }, function () {
                    page.freezeInput(false);
                    $(additionalClass + ' .loading').toggleClass('invisible');
                }
        );
    }, 
    onSubmitPubKey: function (event) {
        var page = event.data;
        var pubkey = $('#pubkey').val();

        $('.additional .error').html("");
        $('.additional .error').hide();

        if (!pubkey.match(/^ssh-(rsa|dss)/)) {
            $('.additional .error').html("Key is invalid. It must begin with 'ssh-rsa' or 'ssh-dss'");
            $('.additional .error').show();
            return false;
        }

        page.uploadTextArea(page, 'ajax/uploadSshPubKey.php', { sid: page.service.sid, sshkey: pubkey }, '.additional');
    },
    onSubmitStartupScript: function (event) {
        var page = event.data;
        var contents = $('#startupscript').val();

        $('.additional .error').html("");
        $('.additional .error').hide();

        page.uploadTextArea(page, 'ajax/uploadStartupScript.php', { sid: page.service.sid, script: contents }, '.additionalStartup');
    },
    onSaveConfig: function (event) {
        var page = event.data,
            params = {phpconf: {
                max_execution_time: $('#conf-maxexec').val(),
                memory_limit: $('#conf-memlim').val(),
                upload_max_filesize: $('#conf-uploadmaxsize').val(),
                post_max_size: $('#conf-postmaxsize').val(),
            }};
        $(event.target).attr('disabled', 'disabled');
        page.updateConfiguration(params, function () {
            $('.settings-form .actions .positive').show();
            setTimeout(function () {
                $('.settings-form .actions .positive').fadeOut();
            }, 2000);
        }, function () {
            $(event.target).removeAttr('disabled');
        });
    },
    onCdsSubscribe: function (event) {
        var page = event.data;
        page.freezeInput(true);
        page.displayInfo('subscribing to CDN...');
        conpaas.ui.visible('subscribe-loading', true);
        page.server.req('ajax/cds_subscribe.php',
                {sid: page.service.sid, cds: $('#cds').val(), subscribe: true},
                'post', function (response) {
                    if (response.subscribe) {
                        window.location.reload();
                    }
                }, function () {
                    page.freezeInput(false);
                })
    },
    onCdsUnsubscribe: function (event) {
        var page = event.data;
        page.freezeInput(true);
        page.displayInfo('unsubscribing from CDN...');
        page.server.req('ajax/cds_subscribe.php',
                {sid: page.service.sid, cds: '', subscribe: false},
                'post', function (response) {
                    if (response.unsubscribe) {
                        window.location.reload();
                    }
                }, function () {
                    page.freezeInput(false);
                });
    },
    /**
     * load the rendered HTML for the versions container
     */
    reloadVersions: function () {
        var that = this;
        this.server.reqHTML('ajax/render.php',
                {sid: this.service.sid, target: 'versions'}, 'get',
                function (response) {
                    $('#versionsWrapper').html(response);
                    $('.versions .activate').click(that,
                            that.onActivateVersion);
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
        page = new conpaas.ui.HostingPage(server, service);
        page.attachHandlers();
        if (page.service.needsPolling()) {
            page.freezeInput(true);
            page.pollState(function () {
                window.location.reload();
            });
        }
    }, function () {
        // error
        window.location = 'index.php';
    })

    // load startup script
    server.req('ajax/getStartupScript.php', {sid: sid}, 'get', 
        function (data) {
            data = JSON.parse(data);

            if (data.error) {
                $('#startupscript').val("# Write your startup script here!");
            }
            else {
                $('#startupscript').val(data.result);
            }
        },
        // error
        function () {}
    );
});
