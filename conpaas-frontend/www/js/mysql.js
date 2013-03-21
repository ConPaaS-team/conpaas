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

conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.MysqlPage
     */
    this_module.MysqlPage = conpaas.new_constructor(
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
        $('#resetPassword').click(this, this.onResetPassword);
        $('#showResetPasswd, #warningResetPasswd').click(function () {
            $('#passwordForm').show();
            $('#resetPasswordForm').show();
            $('#passwd').focus();
        });
        $('.command').click(function () {
            $(this).focus().select();
        });
        $('#dbfile').change(function () {
            $('#loadfile').removeAttr('disabled');
        });
        $('#loadfile').click(function () {
            $('#loadform .loading').show();
            $('#loadform .positive').hide();
            $('#loadform .error').hide();
            $('#loadform').submit();
        });
        $('#loadform').ajaxForm({
            dataType: 'json',
            success: function (response) {
                if (response.error) {
                    that.onLoadFileError(response.error);
                    return;
                }
                $('#loadform .loading').hide();
                $('#loadfile').attr('disabled', 'disabled');
                $('#dbfile').val('');
                $('#loadform .positive').show();
            },
            error: function (response) {
                that.onLoadFileError(response);
            }
        });
    },
    onLoadFileError: function (error) {
        $('#loadform .loading').hide();
        $('#loadform .error').html('Error: <b>' + error + '</b>').show();        
    },
    showResetStatus: function (type, message) {
        var otherType = (type === 'positive') ? 'error' : 'positive';
        $('#resetStatus').removeClass(otherType).addClass(type)
            .html(message)
            .show();
        setTimeout(function () {
            $('#resetStatus').fadeOut();
        }, 3000);
    },
    // handlers
    onResetPassword: function (event) {
        var page = event.data,
            passwd = $('#passwd').val(),
            passwdRe = $('#passwdRe').val(),
            user = $('#user').html();

        if (passwd.length < 8) {
            page.showResetStatus('error', 'Password too short');
            $('#passwd').focus();
            return;
        }
        if (passwd !== passwdRe) {
            page.showResetStatus('error', 'Retyped password does not match');
            $('#passwdRe').focus();
            return;
        }
        // send the request
        $('#resetPassword').attr('disabled', 'disabled');
        page.server.req('ajax/setPassword.php', {
            sid: page.service.sid,
            user: user,
            password: passwd
        }, 'post', function (response) {
            // successful
            page.showResetStatus('positive', 'Password was reset successfuly');
            $('#resetPassword').removeAttr('disabled');
            $('#passwd').val('');
            $('#passwdRe').val('');
            $('.selectHint, .msgbox').hide();
        }, function (response) {
            // error
            page.showResetStatus('error', 'Password was not reset');
            $('#resetPassword').removeAttr('disabled');
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
        page = new conpaas.ui.MysqlPage(server, service);
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
