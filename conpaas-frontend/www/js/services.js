
/* Copyright (C) 2010-2013 by Contrail Consortium. */



/**
 * interaction for application.php - main dashboard
 * @require conpaas.js
 */
conpaas.ui = (function (this_module) {
    this_module.Dashboard = conpaas.new_constructor(
    /* extends */conpaas.ui.Page,
    /* constructor */function (server) {
        this.server = server;
        this.startingApp = false;
        this.poller = new conpaas.http.Poller(server, 'ajax/checkApplications.php', 'get');
        // this.poller = new conpaas.http.Poller(server, 'ajax/checkServices.php', 'get');
    },
    /* methods */{
    /**
     * @param {Service} service that caused the polling to be continued
     */

    displayInfo_: function(info){
        $('#pgstatInfoText').html(info);
        conpaas.ui.visible('pgstatInfo', true);
    },

    displayServiceInfo_: function (service) {
        var info = 'at least one service is in a transient state';
        if (!service.reachable) {
            info = 'at least one service is unreachable'
        }
        this.displayInfo_(info);
    },
    makeRemoveHandler_: function (service) {
        var that = this;
        return function () {
            that.removeService(service);
        };
    },
    saveName: function (newName, onSuccess, onError) {
        this.server.req('ajax/renameApplication.php',
                {name: newName}, 'post',
                onSuccess, onError);
    },
    onClickName: function (event) {
        var page = event.data;
        var newname = prompt("Enter a new name", $('#name').html());
        if (!newname) {
            return;
        }
        page.saveName(newname, function () {
            $('#name').html(newname);
        })
    },
    attachHandlers: function () {
        var that = this;
        conpaas.ui.Page.prototype.attachHandlers.call(this);
        $('#name').click(this, this.onClickName);
        $('#btnStartApp').click(this, this.onClickStartApp);
        $('#btnStopApp').click(this, this.onClickStopApp);
    },
    checkServices: function () {
        var that = this;
        this.poller.setLoadingText('checking services...').poll(
                function (response) {
            var service,
                services,
                i,
                stopPolling = true;
            services = response.data.services;
            $('#servicesWrapper').html(response.html);
            for (i = 0; i < services.length; i++) {
                service = new conpaas.model.Service(services[i].sid,
                        services[i].state, services[i].instanceRoles,
                        services[i].reachable);
                if (service.needsPolling()) {
                    that.displayServiceInfo_(service);
                    stopPolling = false;
                }
                // HACK: attach handlers for delete buttons;
                // without using the id trick we cannot avoid using global vars
                $('#service-' + service.sid + ' .deleteService').click(
                        that.makeRemoveHandler_(service));
            }
            if (response.data.application.status == "ADAPTING")
                stopPolling = false;
                
            conpaas.ui.visible('pgstatInfo', false);
            return stopPolling;
        });
    },
    checkApplication: function(){
        var that = this;
        this.poller.setLoadingText('checking application...').poll(
                function (response) {
                    app = response.data[0];
                    that.application = app;
                    if (app.status == 'INIT' || app.status == 'STOPPED' || app.status == 'PROLOGUE' || app.status == 'EPILOGUE') {
                        $("#btnAddService").hide();
                        $("#btnStopApp").hide();
                        $("#appRightMenu").hide();
                        if (app.status == 'PROLOGUE') {
                            that.displayInfo_('application is starting up...');
                            return false
                        } else if (app.status == 'EPILOGUE') {
                            that.displayInfo_('application is releasing resources...');
                            return false
                        } else {
                            $("#btnStartApp").show();
                            $("#cloudProviders").show();
                        }
                    } else {
                        $("#btnStartApp").hide();
                        $("#cloudProviders").hide();
                        $("#btnAddService").show();
                        $("#btnStopApp").show();
                        $("#appRightMenu").show();
                        html = '<div class="instance dualbox"><div class="left"><i class="title">Instance '+app.cloud+app.vmid+'</i><div class="tag blue">&nbsp;Application manager&nbsp;</div><div class="brief">running</div></div><div class="right"><i class="address">'+app.manager.replace('https://', '')+'</i></div><div class="clear"></div></div>'
                        $("#instances").html(html);
                        that.startingApp = false;
                        that.poller = new conpaas.http.Poller(that.server, 'ajax/checkServices.php', 'get');
                        that.checkServices();
                    }
                    conpaas.ui.visible('pgstatInfo', false);
                    return true
        }, {'aid':1});
    },

    // getAppStatus: function(){
    //     this.server.req('ajax/checkApplications.php', {'aid':1}, 'post', 
    //         function(response){
    //             status = response.data[0].status
    //         }, 
    //         function (){
    //             // page.showStatus('', 'error', 'Something wrong happened');
    //         }, 'json', true
    //     );

    // },

    onClickStartApp: function(event){
        var page = event.data;
        page.startingApp = true;
        $("#btnStartApp").hide();
        $("#cloudProviders").hide();
        page.server.req('ajax/startApplication.php', {
                cloud: $('input[name=available_clouds]:checked').val()
            }, 'post',
            function(){
                page.displayInfo_('starting application manager...');
                page.checkApplication();      
            }, 
            function (){
                page.showStatus('', 'error', 'Something wrong happened');
                page.freezeInput(false);
            }, 'json', true
        );
        // page.displayInfo_('Starting application manager...');
        // page.checkApplication();
        
    },

    onClickStopApp: function(event){
        var page = event.data;
        var r = confirm('Are you sure to stop the application?');
        if (r == false) {
            return;
        }

        page.server.req('ajax/stopApplication.php', {
            aid: page.application.aid
        }, 'post', function (response) {
            window.location = 'index.php';
            return;
        }, function (error) {
            page.displayError(error.name, error.details);
        });
    },

    removeService: function (service) {
        var that = this,
            servicePage = new conpaas.ui.ServicePage(this.server, service);
        servicePage.remove(function () {
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
    page.checkApplication();
    // page.checkServices();

});
