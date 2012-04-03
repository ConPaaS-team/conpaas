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
