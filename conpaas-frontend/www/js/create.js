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

/**
 * interaction for create.php
 * @require conpaas.js, servicepage.js
 */
conpaas.ui = (function (this_module) {
    this_module.CreatePage = conpaas.new_constructor(
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
            $(this).find(':radio').attr('checked', true);
            $('#create').attr('disabled', false);
        });
    },
    onCreate: function (event) {
        var page = event.data,
            button = event.target;
        if ($(button).attr('disabled') === 'disabled') {
            return;
        }
        if (!page.selectedService) {
            return;
        }
        $(button).attr('disabled', 'disabled');
        $(button).removeClass('button');
        $(button).addClass('button-disabled');
        $('#pgstatLoadingText').html('creating service...');
        conpaas.ui.visible('pgstatLoading', true);
        page.server.req('ajax/createService.php', {
            type: page.selectedService.find(':radio').val(),
            cloud: $('#cloud option:selected').val(),
        }, 'post', function (response) {
            var service, servicePage;
            conpaas.ui.visible('pgstatLoading', false);
            if (response.create == 1) {
                service = new conpaas.model.Service(response.sid, 'PREINIT');
                servicePage = new conpaas.ui.ServicePage(page.server, service);
                servicePage.pollState(function () {
                    window.location = 'index.php';
                });
            }
        }, function (response) {
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
        page = new conpaas.ui.CreatePage(server);
    page.attachHandlers();
});
