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
				<img src="images/contrail_paas_logo_large.png" />
			</div>
		</div>
		<div class="formwrap">
		<div class="form">
			<h2 class="title" id="login-title">Login</h2>
			<h2 class="title" id="register-title" style="display: none;">Register</h2>
			<table>
				<tr>
					<td class="name">username</td>
					<td class="input">
						<input type="text" id="username" />
					</td>
				</tr>
				<tr>
					<td></td>
					<td>
						<div class="hint">enter your name or email address</div>
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
						<input type="button" value="register" id="register" 
							style="display: none;" />
						<a id="toregister" href="javascript: void(0);">register</a>
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
		if ($('#username').val() == '') {
			$('#username').focus();
			return;
		}
		$('.login .loading').show();
  		$.ajax({
  			url: 'services/login.php',
  			data: {
	  			action: type,
	  			username: $('#username').val()
  			},
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
			$('#login').toggleClass('active');
			$('#register').toggleClass('active');
			$('#login').hide();
			$('#register').show();
			$('#username').focus();
		});
	});
	</script>
</body>
</html>