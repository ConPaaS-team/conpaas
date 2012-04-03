<?php
/*
 * Copyright (C) 2010-2011 Contrail consortium.
 *
 * This file is part of ConPaaS, an integrated runtime environment
 * for elastic cloud applications.
 *
 * ConPaaS is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * ConPaaS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once('__init__.php');
require_module('ui/page');

if (isset($_SESSION['uid'])) {
	header('Location: index.php');
	exit();
}

$page = new Page();
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>ConPaaS login </title>
<?php echo $page->renderIcon(); ?>
<link type="text/css" rel="stylesheet" href="conpaas.css" />
<script src="js/jquery-1.5.js"></script>
<script src="js/jquery.form.js"></script>
</head>
<body class="loginbody">
	<div class="logo">
		<img src="images/conpaas_large.png" />
	</div>
	<div class="login">
		<table><tr>
		<td class="descr" width="65%">
			<p><b>ConPaaS</b> is the Platform-as-a-Service component of the <a href="http://contrail-project.eu/">Contrail</a> project.</p>
			<p><b>ConPaaS</b> aims at facilitating the deployment of applications in the cloud. It provides a number of services to address common developer needs.
			Each service is self-managed and elastic:
			<ul>
				<li> it can deploy itself on the cloud </li>
				<li> monitor its own performance
				<li> increase or decrease its processing capacity by dynamically (de-)provisioning instances of itself in the cloud </li>
			</ul>
			</p>
		</td>
		<td class="formwrap">
		<div class="form">
			<h2 class="title" id="login-title">Login</h2>
			<h2 class="title invisible" id="register-title">Register</h2>
			<table>
				<tr>
					<td class="name">username</td>
					<td class="input">
						<input type="text" id="username" />
					</td>
				</tr>
				<tr class="register_form" style="display: none">
					<td class="name">email</td>
					<td class="input">
						<input type="text" id="email" />
					</td>
				</tr>
				<tr>
					<td class="name">password</td>
					<td class="input">
						<input type="password" id="passwd" />
					</td>
				</tr>
				<tr class="register_form" style="display: none">
					<td class="name">retype password</td>
					<td class="input">
						<input type="password" id="passwd2" />
					</td>
				</tr>
				<tr class="register_form" style="display: none">
					<td class="name">first name</td>
					<td class="input">
						<input type="text" id="fname" />
					</td>
				</tr>
				<tr class="register_form" style="display: none">
					<td class="name">last name</td>
					<td class="input">
						<input type="text" id="lname" />
					</td>
				</tr>
				<tr class="register_form" style="display: none">
					<td class="name">affiliation</td>
					<td class="input">
						<input type="text" id="affiliation" />
					</td>
				</tr>
				<tr>
					<td class="name">
						<img class="loading invisible" src="images/icon_loading.gif" />
					</td>
					<td class="actions">
						<input class="active" type="button" value="login" id="login" />
						<input type="button" class="invisible" value="register" id="register" />
						<a id="toregister" href="javascript: void(0);">register</a>
					</td>
				</tr>
				<tr>
					<td></td>
					<td><div id="error invisible"></div></td>
				</tr>
			</table>
		</div>
		</td>
		</tr></table>
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
  			url: 'ajax/login.php',
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
			  if ($('#username').val() != "") {
			    $('#passwd').focus();
			  }
			}
		  });
		 $('#passwd').keyup(function(e) {
		     var code = (e.keyCode ? e.keyCode : e.which);
		     if (code == 13) {
		       if ($('#username').val() != "" && $('#passwd').val() != "") {
			 login();
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
			$('#register-title').show();
			$(this).hide();
			$('.register_form').show("slow");
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