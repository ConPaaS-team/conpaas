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
 * interaction for index.php - main dashboard
 * @require conpaas.js
 */
conpaas.ui = (function (this_module) {
    this_module.Dashboard = conpaas.new_constructor(
    /* extends */conpaas.ui.Page,
    /* constructor */function (server) {
        this.server = server;
        this.poller = new conpaas.http.Poller(server, 'ajax/checkServices.php',
                'get');
    },
    /* methods */{
    /**
     * @param {Service} service that caused the polling to be continued
     */
    displayInfo_: function (service) {
        var info = 'at least one service is in a transient state';
        if (!service.reachable) {
            info = 'at least one service is unreachable'
        }
        $('#pgstatInfoText').html(info);
        conpaas.ui.visible('pgstatInfo', true);
    },
    makeDeleteHandler_: function (service) {
        var that = this;
        return function () {
            that.deleteService(service);
        };
    },
    checkServices: function () {
        var that = this;
        this.poller.setLoadingText('checking services...').poll(
                function (response) {
            var service,
                services,
                i,
                continuePolling = true;
            services = response.data;
            $('#servicesWrapper').html(response.html);
            for (i = 0; i < services.length; i++) {
                service = new conpaas.model.Service(services[i].sid,
                        services[i].state, services[i].instanceRoles,
                        services[i].reachable);
                if (service.needsPolling()) {
                    that.displayInfo_(service);
                    continuePolling = false;
                }
                // HACK: attach handlers for delete buttons;
                // without using the id trick we cannot avoid using global vars
                $('#service-' + service.sid + ' .deleteService').click(
                        that.makeDeleteHandler_(service));
            }
            conpaas.ui.visible('pgstatInfo', false);
            return continuePolling;
        });
    },
    deleteService: function (service) {
        var that = this,
            servicePage = new conpaas.ui.ServicePage(this.server, service);
        servicePage.terminate(function () {
            $('#service-' + service.sid).hide();
        }, function () {
            // error
            that.poller.stop();
        });
    }
    });

    return this_module;
}(conpaas.ui || {}));

$(document).ready(function () {
    var server = new conpaas.http.Xhr(),
        page = new conpaas.ui.Dashboard(server);
    page.attachHandlers();
    page.checkServices();
});