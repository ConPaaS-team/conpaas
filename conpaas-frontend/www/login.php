<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */




require_once('__init__.php');
require_module('ui/page/login');
require_module('recaptcha');

if (isset($_SESSION['uid'])) {
    header('Location: index.php');
    exit();
}

$page = new LoginPage();
?>

<?php echo $page->renderDoctype(); ?>
<html>
    <head>
          <?php echo $page->renderContentType(); ?>
        <?php echo $page->renderTitle(' - Login'); ?>
        <?php echo $page->renderIcon(); ?>
        <?php echo $page->renderHeaderCSS(); ?>
    </head>
<body class="loginbody">
    <div class="logo">
        <a href="http://www.conpaas.eu/"><img src="images/conpaas-logo-large.png" /></a>
    </div>
    <div class="login">
        <table><tr>
        <td class="descr" width="65%">
            <p><b><a href="http://www.conpaas.eu/">ConPaaS</a></b> is the Platform-as-a-Service component of the <a href="http://contrail-project.eu/">Contrail</a> E.U. project.</p>
            <p><b>ConPaaS</b> aims at facilitating the deployment of applications in the cloud. It provides a number of services to address common developer needs.
            Each service is self-managed and elastic:
            <ul>
                <li> it can deploy itself on the cloud </li>
                <li> it monitors its own performance </li>
                <li> it can increase or decrease its processing capacity by dynamically <br />(de-)provisioning instances of itself in the cloud </li>
            </ul>
            <em>Copyright &copy;2011-<?php echo date('Y')?> Contrail consortium.<br>All rights reserved.</em>
            </p>
        </td>
        <td class="formwrap">
        <div id="user-form">
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
                        <input type="password" id="password" />
                    </td>
                </tr>
                <tr class="register_form" style="display: none">
                    <td class="name">retype password</td>
                    <td class="input">
                        <input type="password" id="password2" />
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
                <?php
                /* Only enable captcha checks if the required configuration
                 * options are provided */
                if (defined('CAPTCHA_PUBLIC_KEY') && defined('CAPTCHA_PRIVATE_KEY')) {
                 ?>
                <script type="text/javascript">
                    var RecaptchaOptions = {
                        theme : 'white'
                     };
                 </script>
                <tr class="register_form invisible">
                    <td colspan="2" id="recaptcha">
                    <?php echo recaptcha_get_html(CAPTCHA_PUBLIC_KEY); ?>
                    </td>
                </tr>
                <?php
                }
                 ?>
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
                    <td><div id="error"></div></td>
                </tr>
            </table>
            <div id="error" class="invisible"></div>
        </div>
        </td>
        </tr>
        </table>
    </div>
    <?php echo $page->renderJSLoad(); ?>
</body>
</html>
