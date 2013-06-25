
/* Copyright (C) 2010-2013 by Contrail Consortium. */



/**
 * @require conpaas.js, servicepage.js
 */
conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.ServicePage
     */
    this_module.ServicePage = conpaas.new_constructor(
    /* extends */conpaas.ui.Page,
    /* constructor */function (server, service) {
        this.server = server;
        this.service = service;
        this.setupPoller_();
    },
    /* methods */{
    setupPoller_: function () {
        this.statePoller = new conpaas.http.Poller(this.server,
                'ajax/getService.php', 'get');
        this.statePoller.setLoadingText('checking service...');
    },
    displayInfo: function (info) {
        $('#pgstatInfoText').html(info);
        conpaas.ui.visible('pgstatInfo', true);
    },
    displayReason_: function () {
        var reason;
        if (!this.reachable) {
            if (this.service.state === 'PREINIT') {
                reason = 'service created, waiting to start';
            } else if (this.service.state === 'INIT') {
                reason = 'service is starting...';
            } else if (this.service.state === 'PROLOGUE') {
                reason = 'service is starting up...';
            } else if (this.service.state === 'EPILOGUE') {
                reason = 'service is releasing resources...';
            } else if (this.service.state === 'ADAPTING')  {
                reason = 'service is applying changes...'
            } else {
                reason = 'service in transient state ' + this.service.state;
            }
        } else {
            reason = 'service is unreachable in state '
                + this.service.state;
        }
        this.displayInfo(reason);
    },
    freezeButtons: function (buttons, freeze) {
        buttons.forEach(function (id) {
            if (freeze) {
                $('#' + id).attr('disabled', 'disabled');
            } else {
                $('#' + id).removeAttr('disabled');
            }
        });
    },
    pollState: function (onStableState, onInstableState, maxInterval) {
        var that = this;
        this.statePoller.poll(function (response) {
            that.service.state = response.state;
            that.service.reachable = response.reachable;
            if (!that.service.needsPolling()) {
                conpaas.ui.visible('pgstatInfo', false);
                if (typeof onStableState === 'function') {
                    onStableState(response);
                }
                // reached stable state
                return true;
            }
            that.displayReason_();
            // returning false will cause the poller to continue polling
            if (typeof onInstableState === 'function') {
                onInstableState(response);
            }
            return false;
        }, {sid: this.service.sid}, maxInterval);
    },
    freezeInput: function (freeze) {
        var buttons = ['start', 'stop', 'terminate', 'submitnodes', 'file'];
        this.freezeButtons(buttons, freeze);
    },
    terminate: function (onSuccess, onError) {
        this.server.req('ajax/terminateService.php',
                {sid: this.service.sid}, 'post', onSuccess, onError);
    },
    saveName: function (newName, onSuccess, onError) {
        this.server.req('ajax/saveName.php',
                {sid: this.service.sid, name: newName}, 'post',
                onSuccess, onError);
    },
    start: function (onSuccess, onError) {
        this.server.req('ajax/requestStartup.php',
                {sid: this.service.sid,
                 cloud: $('input[name=available_clouds]:checked').val()},
                'post', onSuccess, onError);
    },
    stop: function (onSuccess, onError) {
        this.server.req('ajax/requestShutdown.php', {sid: this.service.sid},
                'post', onSuccess, onError);
    },
    addNodes: function (params, onSuccess, onError) {
        params.sid = this.service.sid;
        radio = $('input[name=available_clouds]:checked');
        if (!radio.size()==1){
           alert("For adding nodes a cloud must be selected");
           page.freezeInput(false);
           return;
        }
        params.cloud = radio.val();
        this.server.req('ajax/addServiceNodes.php', params, 'post',
                onSuccess, onError);
    },
    removeNodes: function (params, onSuccess, onError) {
        params.sid = this.service.sid;
        this.server.req('ajax/removeServiceNodes.php', params, 'post',
                onSuccess, onError);
    },
    updateConfiguration: function (params, onSuccess, onError) {
        params.sid = this.service.sid;
        this.server.req('ajax/sendConfiguration.php', params, 'post',
                onSuccess, onError);
    },
    // handlers
    attachHandlers: function () {
        var that = this;
        conpaas.ui.Page.prototype.attachHandlers.call(this);
        $('#name').click(this, this.onClickName);
        $('#start').click(this, this.onClickStart);
        $('#stop').click(this, this.onClickStop);
        $('#terminate').click(this, this.onClickTerminate);
        this.service.instanceRoles.forEach(function (role) {
            $('#' + role).click(that, that.onInstanceRoleClick);
        });
        $('#submitnodes').click(this, this.onSubmitNodesClick);
    },
    // static handlers
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
    onClickStart: function (event) {
        var page = event.data;
        page.freezeInput(true);
        page.start(function (response) {
            page.displayInfo('command sent, waiting to start...');
            page.pollState(function () {
                window.location.reload();
            });
        }, function (response) {
            page.freezeInput(false);
        });
    },
    onClickStop: function (event) {
        var page = event.data;
        var ack = confirm('Are you sure you want to stop the service?');
        if (!ack) {
            return;
        }
        page.freezeInput(true);
        page.stop(function (response) {
            page.displayInfo('command sent, waiting to stop...');
            page.pollState(function () {
                window.location.reload();
            });
        }, function (response) {
            page.freezeInput(false);
        });
    },
    onClickTerminate: function (event) {
        var page = event.data;
        if (!confirm('After termination, the service will be completely'
                + ' destroyed. Are you sure you want to continue?')) {
            return;
        }
        page.terminate(function (response) {
            window.location = 'services.php';
        });
    },
    onInstanceRoleClick: function (event) {
        var positive,
            prefix,
            allZero,
            value,
            page = event.data;
        value = prompt('no. of instances (e.g. +1, -2)', $(this).html());
        if (!value) {
            return;
        }
        value = +value; // convert to number
        if (isNaN(value)) {
            return;
        }
        // do not allow to add & remove nodes in the same time by zeroing
        // the values that are different with the current input
        function sign (value) {
            if (value > 0) {
                return +1;
            } else if (value < 0) {
                return -1;
            }
            return 0;
        }
        page.service.instanceRoles.forEach(function (role) {
            var otherValue = +$('#' + role).html();
            if (otherValue && sign(value) !== sign(otherValue)) {
                $('#' + role).html('0');
            }
        });
        prefix = (value > 0) ? '+' : '';
        $(this).html(prefix + value);
        allZero = true;
        page.service.instanceRoles.forEach(function (role) {
            if (+$('#' + role).html() !== 0) {
                allZero = false;
            }
        });
        if (allZero) {
            $('#submitnodes').attr('disabled', 'disabled');
        } else {
            $('#submitnodes').removeAttr('disabled');
        }
    },
    onSubmitNodesClick: function (event) {
        var add,
            toChange = {},
            msg = '',
            ack,
            successHandler,
            errorHandler,
            page = event.data;
        // pick values
        page.service.instanceRoles.forEach(function (role) {
            var value = +$('#' + role).html();
            if (value) {
                toChange[role] = (value > 0 ? value : -value);
                add = (value > 0);
                if (msg) {
                    msg += ' and ';
                }
                msg += '' + (value > 0 ? value : -value) + ' ' + role;
            }
        });
        if (add) {
            msg = 'add ' + msg;
        } else {
            msg = 'remove ' + msg;
        }
        ack = confirm('Are you sure you want to ' + msg + ' node(s)?');
        if (!ack) {
            return;
        }
        successHandler = function () {
            page.displayInfo('command sent, waiting to stop...');
            page.pollState(function () {
                window.location.reload();
            });
        };
        errorHandler = function () {
            page.freezeInput(false);
        }
        page.freezeInput(true);
        if (add) {
            page.addNodes(toChange, successHandler, errorHandler);
        } else {
            page.removeNodes(toChange, successHandler, errorHandler);
        }
    }
    });

    return this_module;
}(conpaas.ui || {}));
