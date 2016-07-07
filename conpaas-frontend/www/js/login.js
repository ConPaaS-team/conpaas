conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.LoginPage
     */
    this_module.LoginPage = conpaas.new_constructor(
    /* extends */Object,
    /* constructor */function (server) {
        this.server = server;
        this.state = 'login';
    },
    /* methods */{
    attachHandlers: function () {
        var that = this;
        $('#toregister').click(this, this.onShowRegister);
        $('#togoback').click(this, this.onShowLogin);
        $('#login').click(this, this.onLogin);
        $('#clearForm').click(this, this.onClearForm);
        $('#but_contrail').click(this, this.onContrail);
        $('#but_openid').click(this, this.onOpenID);
        $('#register').click(this, this.onRegister);
        // attach keyboard shortcuts
        $('#username, #password').keyup(function (event) {
            var code = (event.keyCode ? event.keyCode : event.which),
                target = event.target;
            if (code === 13) {
                if (document.getElementById('username') === target) {
                    if ($(target).val()) {
                        $('#password').focus();
                    }
                    return;
                }
                if (document.getElementById('password') === target) {
                    if ($(target).val()) {
                        that.onLogin({data: that});
                    }
                    return;
                }
                if ($('#username').val()) {
                    $('#password').focus();
                }
            }
        });
    },
    validateNonemptyFields: function(fields) {
        var i, key;
        for (i = 0; i < fields.length; i += 1) {
            key = fields[i];
            if (!$('#' + key).val()) {
                $('#' + key).focus();
                return false;
            }
        }
        return true;
    },
    displayError: function(title, details) {
        var tail = details ? ': ' + details : '';
        $('#error').html(title + tail);
        $('#error').removeClass('invisible');
    },
    // handlers
    onClearForm: function (event) { // #clearForm
        var page = event.data;
        $("#fname").val( ' ' );
        $("#lname").val( ' ' );
        $("#roles").val( ' ' );
        $("#groups").val( ' ' );
        //$("#uuid").val( '<none>' );
        //$("#openid").val( '<none>' );
        //$("#selected").val( '<none>' );
    },
    onShowRegister: function (event) { // #toregister
        var page = event.data;
        page.state = 'register';
        $(document).attr('title', 'ConPaaS - management interface - Register');
        $('#login-title').hide('slow');
        $('#register-title').show();
        $(this).hide();
        $('#togoback').show();
        $('.register_form').show('slow');
        $('#login').toggleClass('active');
        $('#register').toggleClass('active');
        $('#login').hide();
        $('#register').show();
        $('#but_contrail').addClass('invisible');
        $('#but_openid').addClass('invisible');
        $('#uuid').removeClass('invisible'); // remove later
        $('#openid').removeClass('invisible'); // remove later
        $('#selected').removeClass('invisible'); // remove later

        $('#username').focus();
        $('.login .form').width(320);
    },
    onShowLogin: function (event) { // #togoback
        var page = event.data;
        page.state = 'login';
        $(document).attr('title', 'ConPaaS - management interface - Login');
        $('#login-title').show();
        $('#register-title').hide('slow');
        $(this).hide();
        $('#toregister').show();
        $('.register_form').hide();
        $('#login').toggleClass('active');
        $('#register').toggleClass('active');
        $('#login').show();
        $('#register').hide();
        $('#but_contrail').removeClass('invisible');
        $('#but_openid').removeClass('invisible');
        $('#uuid').addClass('invisible'); // remove later
        $('#openid').addClass('invisible'); // remove later
        $('#selected').addClass('invisible'); // remove later

        $('#username').focus();
        $('.login .form').width(320);
    },
    onLogin: function (event) {
        var page = event.data,
            username = $('#username').val(),
            password = $('#password').val();
        if (!page.validateNonemptyFields(['username', 'password'])) {
            return;
        }
        $('#error').addClass('invisible');
        page.server.req('ajax/authenticate.php', {
            username: username, password: password
        }, 'post', function (response) {
            if (response.authenticated == 1) {
                debug_alert('Passed login, show index');
                window.location = 'index.php';
                return;
            }
            page.displayError('user and/or password not matched')
        }, function (error) {
            page.displayError(error.name, error.details);
        });
    },
    onContrail: function (event) {
        debug_alert('Start onContrail');
        var page = event.data;
        var name = $('#name').val();
        var pwd = $('#pwd').val();
        //console.log('ajax start');
        request = $.ajax(
            {
            async: false,
            type: "POST",
            url: "contrail/contrail-idp.php",
            // data: {username:name, password:pwd, ReturnTo:MyURL, get:"get"}
            data: {ReturnTo:MyURL}
            }
        );
        request.done(
            function( response, textStatus, jqXHR  ) {
                //console.log('ajax done');
                //$("#toregister").click();
                $("#msgc").html( " Contrail result for " +name +" is "+response );
                debug_alert('done response = ' + response);
                var resar = eval("(" +  response + ")" );
                var uid = resar["uid"][0];
                var re = /..*@..*\...*/; // match at least  x@y.z  as an e-mail address
                if (re.exec(uid) == null) {
                    $("#username").val ( uid );
                } else {
                    $("#email").val ( uid );
                }
                $("#fname").val( resar["displayName"][0] );
                $("#lname").val( resar["displayName"][1] );
                $("#roles").val( resar["roles"][0] );
                $("#groups").val( resar["groups"][0] );
                $("#uuid").val( resar["uuid"][0] );
                $("#msgl").html("hahaha");
                // $("#selected").val("uuid");
                var uuid = $("#uuid").val();
                //console.log('onContrail: check if uuid ' + uuid + ' present');
                if (uuid) {
                            $("#clearForm").click(); // does this work??
                    page.server.req('ajax/authenticate.php', {
                        uuid: uuid
                    }, 'post', function (response) {
                //$("#selected").val("uuid");
                        console.log('onContrail: response');
                        if (response.authenticated == 1) {
                            debug_alert('Passed uuid login, show index');
                            window.location = 'index.php';
                            return;
                        }
                        page.displayError('user and/or password not matched');
                    }, function (error) {
                        //console.log('onContrail: error');
                        page.displayError('Please fill in all other fields to register.<br>Password may differ from IdP password');
                        //page.displayError(error.name, error.details);
                    });
                } else {
                    $("#toregister").click();
                }
            }
        );
        request.fail(
            function (jqXHR, textStatus, errorThrown) {
                jqXHRobj = JSON.stringify(jqXHR);
                console.log('ajax fail');
                responseHeader = jqXHR.getAllResponseHeaders();
                jsonResponseHeader = JSON.stringify(responseHeader);
                $("#msgl").html( " Contrail error for (name:) " + name + " is (jqXHR:) " + jqXHRobj 
                    + " -- (textStatus:) " + textStatus
                    + " -- (errorThrown:) " + errorThrown
                    + " -- (responseHeader:) " + jsonResponseHeader
                    );
                debug_alert('fail response = ' + jsonResponseHeader);
                $("#ReturnTo").val(MyURL);
                $("#4get").val("4get");
                $("#4set").val("uuid");
                //$("#selected").val("uuid");
                debug_alert('form = ' + $("#form").val() + '\nselected = ' + $("#selected").val() );
                $("#form").submit();  // now go to the multi-login URL
            }
        );
    },
    //======
    onOpenID: function (event) {
        debug_alert('Start onOpenID');
        var page = event.data;
        var name = $('#name').val();
        var pwd = $('#pwd').val();
                $("#ReturnTo").val(MyURL);
                $("#4get").val("4get");
                $("#4set").val("openid");
                $("#selected").val("openid");
                debug_alert('form = ' + $("#form2").val() + $("#form2").attr('action') + '\nselected = ' + $("#selected").val() );
        $('#form2').submit();
        return;
        //console.log('ajax start');
        o_request = $.ajax(
            {
            async: false,
            type: "POST",
            // url: "contrail/contrail-idp.php",
            url: "idp.php",
            // data: {username:name, password:pwd, ReturnTo:MyURL, get:"get"}
            data: {ReturnTo:MyURL}
            }
        );
        o_request.done(
            function( response, textStatus, jqXHR  ) {
                //console.log('ajax done');
                //$("#toregister").click();
                $("#msgc").html( " OpenID result for " +name +" is "+response );
                debug_alert('done response = ' + response);
                var resar = eval("(" +  response + ")" );
                var uid = resar["uid"][0];
                var re = /..*@..*\...*/; // match at least  x@y.z  as an e-mail address
                if (re.exec(uid) == null) {
                    $("#username").val ( uid );
                } else {
                    $("#email").val ( uid );
                }
                $("#fname").val( resar["displayName"][0] );
                $("#lname").val( resar["displayName"][1] );
                $("#roles").val( resar["roles"][0] );
                $("#groups").val( resar["groups"][0] );
                $("#openid").val( resar["uuid"][0] );   // abuse
                $("#msgl").html("hahaha");
                // $("#selected").val("openid");
                var openid = $("#openid").val();
                //console.log('onOpenID: check if openid ' + openid + ' present');
                if (openid) {
                            $("#clearForm").click(); // does this work??
                    page.server.req('ajax/authenticate.php', {
                        openid: openid
                    }, 'post', function (response) {
                //$("#selected").val("openid");
                        console.log('onOpenID: response');
                        if (response.authenticated == 1) {
                            debug_alert('Passed openid login, show index');
                            window.location = 'index.php';
                            return;
                        }
                        page.displayError('user and/or password not matched');
                    }, function (error) {
                        //console.log('onOpenID: error');
                        page.displayError('Please fill in all other fields to register.<br>Password may differ from IdP password');
                        //page.displayError(error.name, error.details);
                    });
                } else {
                    $("#toregister").click();
                }
            }
        );
        o_request.fail(
            function (jqXHR, textStatus, errorThrown) {
                jqXHRobj = JSON.stringify(jqXHR);
                console.log('ajax fail');
                responseHeader = jqXHR.getAllResponseHeaders();
                jsonResponseHeader = JSON.stringify(responseHeader);
                $("#msgl").html( " OpenID error for (name:) " + name + " is (jqXHR:) " + jqXHRobj 
                    + " -- (textStatus:) " + textStatus
                    + " -- (errorThrown:) " + errorThrown
                    + " -- (responseHeader:) " + jsonResponseHeader
                    );
                debug_alert('fail response = ' + jsonResponseHeader);
                $("#ReturnTo").val(MyURL);
                $("#4get").val("4get");
                $("#4set").val("openid");
                //$("#selected").val("openid");
                debug_alert('form = ' + $("#form2").val() + '\nselected = ' + $("#selected").val() );
                $("#form2").submit();  // now go to the multi-login URL
            }
        );
    },
    onRegister: function (event) {
        var page = event.data;
        if (!page.validateNonemptyFields(['username', 'email', 'password', 'password2', 'fname', 'lname', 'affiliation'])) {
            return;
        }
        if ($('#password').val() !== $('#password2').val()) {
            page.displayError('password must match with the retyped one');
            $('#password2').focus().select();
            return;
        }
        // recaptcha_response_field is required only if captcha checks are
        // enabled (ie: #recaptcha_image is defined)
        if ($('#recaptcha_image').length && !page.validateNonemptyFields(['recaptcha_response_field'])) {
            return;
        }
        page.server.req('ajax/register.php', {
            username: $('#username').val(),
            password: $('#password').val(),
            email: $('#email').val(),
            fname: $('#fname').val(),
            lname: $('#lname').val(),
            affiliation: $('#affiliation').val(),
            uuid: $('#uuid').val(),
            openid: $('#openid').val(),
            recaptcha_response: $('#recaptcha_response_field').val(),
            recaptcha_challenge: $('#recaptcha_challenge_field').val()
        }, 'post', function (response) {
            if (!response.registered) {
                if (response.message) {
                    page.displayError(response.message);
                }
                if (response.recaptcha) {
                    Recaptcha.reload();
                }
                return;
            }
            debug_alert('Passed registration, show index');
            window.location = 'index.php';
        }, function (error) {
            page.displayError(error.name, error.details);
        });
    }
    });

    return this_module;
}(conpaas.ui || {}));

$(document).ready(function () {
    var page,
        server = new conpaas.http.Xhr();
    page = new conpaas.ui.LoginPage(server);
    page.attachHandlers();
    $('#username').focus();
    /*
    if (jPosts["4get"] == "4get" || jGets["4get"] == "4get") {
        if (jPosts["4set"]) { $('#selected').val(jPosts["4set"]) ; } 
        if (jGets["4set"]) { $('#selected').val(jGets["4set"]) ; } 
        //$('#toregister').click();
        button = '#error';
        if ($('#selected').val() == "uuid") { button = '#but_contrail' }
        if ($('#selected').val() == "openid") { button = '#but_openid' }
        debug_alert('4get:select ' + $('#selected').val() + '\nbutton = "' + button + '"');

        $(button).click();
        //$('#but_contrail').click();
    }
    */
});
