<?php 

require_once('__init__.php');

if (isset($_SESSION['uid'])) {
	header('Location: index.php');
	exit();
}

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>ConPaaS - configure PHP Service</title>
<link type="text/css" rel="stylesheet" href="conpaas.css" />
<script src="js/jquery-1.5.js"></script>
<script src="js/jquery.form.js"></script>
</head>
<body class="loginbody">
	<div class="login">
		<div class="descr">
			<div class="logo" style="text-align: center;">
				<a href="http://www.conpaas.eu/"><img src="images/contrail_paas_logo_large.png" border=0 /></a>
			</div>
		</div>
		<div class="formwrap">
		<div class="form">
			<h2 class="title" id="login-title">Login</h2>
			<h2 class="register_form" align="center" id="register-title" style="display: none;">Register a new user</h2>
<p class="register_form" style="display: none"><blink>Attention:</blink> <font color="red"> new accounts have zero credit.</font><br>
                                               This means you cannot use the system yet.<br> 
                                               You will receive free credit after we review<br>
                                               your registration.</p>
			<table>
				<tr>
					<td class="name">Username</td>
					<td class="input">
						<input type="text" id="username" style="width:170px" />
					</td>
				</tr>
				<tr class="register_form" style="display: none">
					<td class="name">Email</td>
					<td class="input">
						<input type="text" id="email" style="width:170px" />
					</td>
				</tr>
				<tr>
					<td class="name">Password</td>
					<td class="input">
						<input type="password" id="passwd" style="width:172px" onkeypress="return enterKey(event,this.form)" />
					</td>
				</tr>
				<tr class="register_form" style="display: none">
					<td class="name">Confirm password</td>
					<td class="input">
						<input type="password" id="passwd2" style="width:172px" />
					</td>
				</tr>
				<tr class="register_form" style="display: none">
					<td class="name">First name</td>
					<td class="input">
						<input type="text" id="fname" style="width:170px" />
					</td>
				</tr>
				<tr class="register_form" style="display: none">
					<td class="name">Last name</td>
					<td class="input">
						<input type="text" id="lname" style="width:170px" />
					</td>
				</tr>
				<tr class="register_form" style="display: none">
					<td class="name">Affiliation</td>
					<td class="input">
						<input type="text" id="affiliation"  style="width:170px" />
					</td>
				</tr>
				<tr>
					<td></td>
					<td>
						<div class="hint">Enter your name or email address</div>
					</td>
				</tr>
				<tr>
					<td class="name">
						<img class="loading" src="images/icon_loading.gif"
							style="display: none;" />
					</td>
					<td>
						<input class="active" type="button" value="login" 
							id="login" />
						<input type="button" value="Register" id="register" 
							style="display: none;" />
						<a id="toregister" href="javascript: void(0);">New user</a>
					</td>
				</tr>
				<tr>
					<td> </td>
					<td>
						<div id="error" style="display: none;">
							
						</div> 
					</td>
				</tr>
			</table>
		</div>
		</div>
	</div>

	<script type="text/javascript">

	/*
	 * type can be 'auth' or 'register'
	 * success is the callback function, in case of normal response 
	 */
	function userRequest(type, success) {
		if (type == 'register') {
			fields = ['#username', '#email', '#passwd', '#passwd2', '#fname', '#lname','#affiliation'];
			if ($('#passwd').val() != $('#passwd2').val()) {
				$('#error').html('Passwords do not match').show();
				setTimeout("$('#error').fadeOut();", 2000);
				return;
			}
			$data = {
	  			action: type,
	  			username: $('#username').val(),
	  			email: $('#email').val(),
	  			passwd: $('#passwd').val(),
	  			fname: $('#fname').val(),
	  			lname: $('#lname').val(),
	  			affiliation: $('#affiliation').val()
  			};
		}
		else {
			fields = ['#username', '#passwd'];
			$data = {
	  			action: type,
	  			username: $('#username').val(),
	  			passwd: $('#passwd').val(),
  			}
		}
		for (i in fields) {
    		if ($(fields[i]).val() == '') {
    			$(fields[i]).focus();
    			return;
    		}
		}
		
		$('.login .loading').show();
  		$.ajax({
  			url: 'services/login.php',
  			data: $data,
  			dataType: 'json',
  			type: 'post',
			success: function (response) {
	  			$('.login .loading').hide();
				if (typeof response.error != 'undefined') {
					$('#error').html(response.error).show();
					setTimeout("$('#error').fadeOut();", 2000);
					$('#username').select().focus();
				} else {
					success(response); 
				}
			}
		});
	}

	function login() {
		userRequest('auth', function (response) {
			if (response.auth == 1){
				window.location = 'index.php';
			}
		});
	}
	
	function register() {
		userRequest('register', function (response) {
			if (response.register == 1) {
				window.location = 'index.php';
			}
		});
	}
	
	$(document).ready(function() {
		$('#username').focus();
		$('#username').keyup(function(e) {
			var code = (e.keyCode ? e.keyCode : e.which);
			if (code == 13) {
				if ($('#login').hasClass('active')) {
					login();
				} else {
					register();
				}
			}
		});
		
		$('#login').click(function() {
			login();
		});

		$('#register').click(function() {
			register();
		});

		$('#toregister').click(function() {
			$('#login-title').hide("slow");
			$(this).hide();
			$('.register_form').show("slow");
			$('#login').toggleClass('active');
			$('#register').toggleClass('active');
			$('#login').hide();
			$('#register').show();
			$('#username').focus();
		});

	});

        function enterKey(event,ourform) {
	  if (event && event.which == 13) {
	    login();
	  }
	  else {
	    return true;
	  }
	}

	</script>
</body>
</html>