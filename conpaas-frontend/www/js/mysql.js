
/* Copyright (C) 2010-2013 by Contrail Consortium. */



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
