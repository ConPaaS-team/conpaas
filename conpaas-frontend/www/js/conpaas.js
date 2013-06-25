
/* Copyright (C) 2010-2013 by Contrail Consortium. */



/**
 * provide compatibility with ECMAScript 3; these should be standard equipment
 * in ECMAScript 5.
 * 
 * Before updating this file please document well on JavaScript. We recommend
 * any material by Douglas Crockford, including the book "JavaScript: The Good
 * Parts" and the series of talks "Crockford on JavaScript"[1].
 * 
 * [1] http://www.youtube.com/watch?v=JxAXlJEmNMg
 */

/**
 * Object.keys()
 */
if (!Object.hasOwnProperty('keys')) {
    Object.keys = function (obj) {
        var key, keys = [];
        for (key in obj) {
            if (Object.prototype.hasOwnProperty.call(obj, key)) {
                keys.push(key);
            }
        }
        return keys;
    }
}

/**
 * Object.create()
 */
if (!Object.hasOwnProperty('create')) {
    Object.create = function (object, properties) {
        var result;
        function F() {}
        F.prototype = object;
        result = new F();
        if (properties !== undefined) {
            Object.defineOwnProperties(object, properties);
        }
        return result;
    }
}

/**
 * Array.prototype.forEach()
 */
if (!Array.prototype.hasOwnProperty('forEach')) {
    Array.prototype.forEach = function (func, thisp) {
        var i,
            length = this.length;
        for (i = 0; i < length; i+= 1) {
            if (this.hasOwnProperty(i)) {
                func.call(thisp, this[i], i, this);
            }
        }
    }
}

/**
 * global namespace for ConPaaS JavaScript
 */
var conpaas = (function (this_module) {
    /**
     * Generic function for handling inheritance
     * @param {Object} object inheriting from
     * @param {Function} constructor method
     * @param {Object} object containing the methods of the class
     * @return {Function} the constructor you can used for instantiation
     */
    this_module.new_constructor = function (extend, init, methods) {
        var func, prototype = Object.create(extend && extend.prototype);
        if (methods) {
            Object.keys(methods).forEach(function (name) {
                prototype[name] = methods[name];
            });
        }
        func = function () {
            var that = Object.create(prototype);
            if (typeof init === 'function') {
                init.apply(that, arguments);
            }
            return that;
        }
        func.prototype = prototype;
        prototype.constructor = func;
        return func;
    };

    return this_module;
}(conpaas || {}));

conpaas.ui = (function (this_module) {
    /**
     * make an ui element visible or not visible
     * @param {String} id of the DOM element
     * @param {Boolean} true if we want to make it visible
     */
    this_module.visible = function (id, visible) {
        var selector = '#' + id;
        if (visible) {
            $(selector).show();
        } else {
            $(selector).hide();
        }
    };

    return this_module;
}(conpaas.ui || {}));

conpaas.http = (function (this_module) {
    /**
     * Async connection to the server
     * @provide conpaas.http.Xhr
     */
    this_module.Xhr = conpaas.new_constructor(
    /* extends */Object,
    /* constructor */function () {
    },
    /* methods */{
    handleError: function (error) {
        $('#pgstatErrorName').html(error.name);
        $('#pgstatErrorDetails').click(function () {
            alert(error.details);
        });
        conpaas.ui.visible('pgstatError', true);
        conpaas.ui.visible('pgstatInfo', false);
    },
    req: function (url, params, method, responseCallback, errorCallback,
            dataType) {
        var that = this,
            params = params || {},
            method = method || 'get',
            dataType = dataType || 'json';
        conpaas.ui.visible('pgstatError', false);
        $.ajax({
            url: url,
            type: method,
            dataType: dataType,
            data: params,
            success: function (response) {
                //handle error sent
                if (response.error) {
                    error = {name: 'service error', details: response.error};
                    that.handleError(error);
                    if (typeof errorCallback === 'function') {
                        errorCallback(error);
                    }
                    return;
                }
                responseCallback(response);
            },
            error: function (response) {
                error = {name: 'request error',
                        details: "\nstatus: " + response.status + '; '
                        + "\nresponse:\n" + response.responseText
                };
                that.handleError(error)
                if (typeof errorCallback === 'function') {
                    errorCallback(error);
                }
            }
        })
    },
    reqHTML: function (url, params, method, responseCallback, errorCallback) {
        this.req(url, params, method, responseCallback, errorCallback, 'html');
    }
    });
    /**
     * Poller type: polls a given URL until a condition is met
     * @provide conpaas.http.Poller
     */
    this_module.Poller = conpaas.new_constructor(
    /* extends */Object,
    /* constructor */function (server, url, method) {
        this.server = server;
        this.url = url;
        this.method = method;
        this.loadingText_ = 'checking...';
        this.reset();
        this._showTimer = true;
    },
    /* methods */{
        showTimer: function (show) {
            this._showTimer = show;
            return this;
        },
        setLoadingText: function (text) {
            this.loadingText_ = text;
            return this;
        },
        stop: function () {
            if (!this.isActive()) {
                return;
            }
            clearTimeout(this.timerId_);
            conpaas.ui.visible('pgstatLoading', false);
            conpaas.ui.visible('pgstatTimer', false);
            this.reset();
        },
        isActive: function () {
            return this.timerId_ !== null;
        },
        reset: function () {
            this.pollInterval_ = 2; // seconds
            this.pollRemaining_ = 0; // seconds
            this.timerId_ = null;
            return this;
        },
        poll: function (condition, params, maxInterval) {
            var params = params || {};
            var maxInterval = maxInterval || 16;
            var that = this;
            $('#pgstatLoadingText').html(this.loadingText_);
            conpaas.ui.visible('pgstatLoading', true);
            this.server.req(this.url, params, this.method,
                    function (response) {
                var tick;
                conpaas.ui.visible('pgstatLoading', false);
                if (condition(response)) {
                    // the condition has been met, so the polling stops
                    that.reset();
                    return;
                }
                // roll down the counter
                that.pollRemaining_ = that.pollInterval_;
                if (that.pollInterval_ < maxInterval) {
                    that.pollInterval_ *= 2;
                }
                // we need to do additional polling
                tick = function () {
                    if (that.pollRemaining_ > 0) {
                        $('#pgstatTimerSeconds').html(that.pollRemaining_);
                        if (that._showTimer) {
                            conpaas.ui.visible('pgstatTimer', true);
                        }
                        that.pollRemaining_ -= 1;
                        that.timerId_ = setTimeout(tick, 1000);
                        return;
                    }
                    conpaas.ui.visible('pgstatTimer', false);
                    that.poll(condition, params, maxInterval);
                };
                // initiate timer cascade
                that.timerId_ = setTimeout(tick, 1000);
            });
        }
    });
    
    return this_module;
}(conpaas.http || {}));

conpaas.model = (function (this_module) {
    /**
     * conpaas.model.Service
     */
    this_module.Service = conpaas.new_constructor(
    /* extends */Object,
    /* constructor */function (sid, state, instanceRoles, reachable) {
        this.sid = sid;
        this.state = state;
        this.instanceRoles = instanceRoles || [];
        this.reachable = reachable || false;
    },
    /* methods */{
        /**
         * @return {Boolean} true if the current state is stable
         */
        inStableState: function () {
            return this.state !== 'PROLOGUE' &&
                this.state !== 'EPILOGUE' &&
                this.state !== 'ADAPTING' &&
                this.state !== 'PREINIT';
        },
        /**
         * @return {Boolean} true if you need to poll on this service
         */
        needsPolling: function () {
            return !(this.reachable && this.inStableState());
        }
    });

    /**
     * conpaas.model.Application
     */
    this_module.Application = conpaas.new_constructor(
    /* extends */Object,
    /* constructor */function (aid) {
        this.aid = aid;
    });

    return this_module;
}(conpaas.model || {}));

conpaas.ui = (function (this_module) {
    this_module.Page = conpaas.new_constructor(
    /* extends */Object,
    /* constructor */function (server) {
        this.server = server;
    },
    /* methods */{
    attachHandlers: function () {
        var that = this;
        $('#logout').click(function () {
            that.server.req('ajax/logout.php', {}, 'post',
                    function () {
                window.location = 'index.php';
                });
            });
    }
    });

    this_module.ProgressBar = conpaas.new_constructor(
    /* extends */Object,
    /* constructor */function (containerId) {
        this.containerId = containerId;
        this.ratio =
            ($('#' + containerId + ' .progresswrapper').width() - 4) / 100;
        this.progressElement = $('#' + this.containerId + ' .progress');
        this.valueElement = $('#' + this.containerId + ' .percent');
        this.init();
    },
    /* methods */{
    init: function () {
        this.valueElement.html('0%');
        this.progressElement.width(1);
    },
    setPercent: function (percent) {
        if (!percent) {
            this.valueElement.html('0%');
            return;
        }
        percent = Math.floor(percent);
        if (percent == 0) {
            this.init();
            return;
        }
        this.valueElement.html(percent + '%');
        this.progressElement.width(Math.ceil(percent * this.ratio));
    }
    });

    return this_module;
}(conpaas.ui || {}));
