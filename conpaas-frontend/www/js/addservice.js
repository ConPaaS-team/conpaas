
/* Copyright (C) 2010-2013 by Contrail Consortium. */



/**
 * interaction for addservice.php
 * @require conpaas.js, service.js
 */
conpaas.ui = (function (this_module) {
    this_module.AddServicePage = conpaas.new_constructor(
    /* extends */conpaas.ui.Page,
    /* constructor */function (server) {
        this.server = server;
        this.selectedService = null;
    },
    /* methods */{
    attachHandlers: function () {
        var that = this;
        conpaas.ui.Page.prototype.attachHandlers.call(this);
        $('#create').click(this, this.onCreate);
        $('.createpage .form .service').click(function () {
            if (that.selectedService === $(this)) {
                return;
            }
            if (that.selectedService) {
                that.selectedService.removeClass("selectedservice");
                that.selectedService.addClass("service");
            }
            that.selectedService = $(this);
            $(this).removeClass("service");
            $(this).addClass("selectedservice");
            $(this).find(':radio').prop('checked', true);
            $('#create').prop('disabled', false);
        });
    },
    onCreate: function (event) {
        var page = event.data,
            button = event.target;
        if ($(button).prop('disabled') === 'disabled') {
            return;
        }
        if (!page.selectedService) {
            return;
        }
        $(button).prop('disabled', 'disabled');
        $(button).removeClass('button');
        $(button).addClass('button-disabled');
        $('#pgstatLoadingText').html('adding service...');
        conpaas.ui.visible('pgstatLoading', true);
        page.server.req('ajax/addService.php', {
            type: page.selectedService.find(':radio').val()
        }, 'post', function (response) {
            var service, servicePage;
            conpaas.ui.visible('pgstatLoading', false);
            if (response.create == 1) {
                service = new conpaas.model.Service(response.sid, 'PREINIT');
                servicePage = new conpaas.ui.ServicePage(page.server, service);
                servicePage.pollState(function () {
                    window.location = 'application.php';
                });
            }
        }, function (response) {
            conpaas.ui.visible('pgstatLoading', false);
            $(button).removeAttr('disabled');
            $(button).removeClass('button-disabled');
            $(button).addClass('button');
        });
    },
    });

    return this_module;
}(conpaas.ui || {}));

$(document).ready(function () {
    var server = new conpaas.http.Xhr(),
        page = new conpaas.ui.AddServicePage(server);
    page.attachHandlers();
});
