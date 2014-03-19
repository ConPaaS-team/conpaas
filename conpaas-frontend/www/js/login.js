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
        $('#login').click(this, this.onLogin);
        $('#contrail').click(this, this.onContrail);
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
    onShowRegister: function (event) {
        var page = event.data;
        page.state = 'register';
        $(document).attr('title', 'ConPaaS - management interface - Register');
        $('#login-title').hide('slow');
        $('#register-title').show();
        $(this).hide();
        $('.register_form').show('slow');
        $('#login').toggleClass('active');
        $('#register').toggleClass('active');
        $('#login').hide();
        $('#register').show();
        $('#contrail').addClass('invisible');
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
                window.location = 'index.php';
                return;
            }
            page.displayError('user and/or password not matched')
        }, function (error) {
            page.displayError(error.name, error.details);
        });
    },
    onContrail: function (event) {
        var page = event.data;
        var name = $('#name').val();
        var pwd = $('#pwd').val();
        //console.log('ajax start');
        request = $.ajax(
            {
            async: false,
            type: "POST",
            url: "contrail/contrail-idp.php",
            data: {username:name, password:pwd, ReturnTo:MyURL, get:"get"}
            }
        );
        request.done(
            function( response, textStatus, jqXHR  ) {
                //console.log('ajax done');
                $("#toregister").click();
                $("#msgc").html( " Contrail result for " +name +" is "+response );
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
                var uuid = $("#uuid").val();
                //console.log('onContrail: check if uuid ' + uuid + ' present');
                if (uuid) {
                    page.server.req('ajax/authenticate.php', {
                        uuid: uuid
                    }, 'post', function (response) {
                        //console.log('onContrail: response');
                        if (response.authenticated == 1) {
                            window.location = 'index.php';
                            return;
                        }
                        page.displayError('user and/or password not matched');
                    }, function (error) {
                        //console.log('onContrail: error');
                        page.displayError('Please fill in all other fields to register.<br>Password may differ from IdP password');
                        //page.displayError(error.name, error.details);
                    });
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
                $("#ReturnTo").val(MyURL);
                $("#get").val("get");
                $("#form").submit();
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
    if (jPosts["get"] == "get" || jGets["get"] == "get") {
        $('#toregister').click();
        $('#contrail').click();
    }
});
