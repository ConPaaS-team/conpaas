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
 * interaction for index.php - main application
 * @require conpaas.js
 */
conpaas.ui = (function (this_module) {
    this_module.Application = conpaas.new_constructor(
    /* extends */conpaas.ui.Page,
    /* constructor */function (server) {
        this.server = server;
        this.poller = new conpaas.http.Poller(server, 'ajax/checkApplications.php',
                'get');
    },
    /* methods */{
    makeDeleteHandler_: function (application) {
        var that = this;
        return function () {
            that.deleteApplication(application);
        };
    },
    makeCreateHandler_: function (application) {
        var that = this;
        return function () {
            that.createApplication(application);
        };
    },
    checkApplications: function () {
        var that = this;
        this.poller.setLoadingText('checking applications...').poll(
                function (response) {
            var application,
                applications,
                i;
            applications = response.data;
            $('#servicesWrapper').html(response.html);
            for (i = 0; i < applications.length; i++) {
                application = new conpaas.model.Application(applications[i].aid);
                // HACK: attach handlers for delete buttons;
                // without using the id trick we cannot avoid using global vars
		$('.deleteApplication-' + application.aid).click(
                        that.makeDeleteHandler_(application));
            }
            $('#newapp').click(that.makeCreateHandler_(application));
            conpaas.ui.visible('pgstatInfo', false);

	    return true; /* Never do polling */
        });
    },
    createApplication: function (application) {
	var newapp = prompt("Application name : ", "New Application");
	this.server.req('ajax/createApplication.php', {
		name: newapp
	}, 'post', function (response) {
		window.location = 'index.php';
		return;
	}, function (error) {
		page.displayError(error.name, error.details);
	});
    },
    deleteApplication: function (application) {
	console.log(application);
	this.server.req('ajax/deleteApplication.php', {
		aid: application.aid
	}, 'post', function (response) {
		window.location = 'index.php';
		return;
	}, function (error) {
		page.displayError(error.name, error.details);
	});
    }
    });

    return this_module;
}(conpaas.ui || {}));

$(document).ready(function () {
    var server = new conpaas.http.Xhr(),
        page = new conpaas.ui.Application(server);
    page.attachHandlers();
    page.checkApplications();
});
