/*
 * Copyright (C) 2010-2012 Contrail consortium.
 *
 * This file is part of ConPaaS, an integrated runtime environment
 * for elastic cloud applications.
 *
 * ConPaaS is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * ConPaaS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.
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
        $('#showResetPasswd').click(function () {
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
        window.location = 'index.php';
    })
});