<html>
<!-- file = conpaas-frontend/www/contrail-loggedout.php -->
<head>
<script>
<?php
$realReturn = '/contrail/contrail.php'; // default
if (isset($_GET['returnTo'])) {
        $realReturn = $_GET['returnTo'];
} elseif (isset($_POST['returnTo'])) {
        $realReturn = $_POST['returnTo'];
}
?>
var seconds = 10;
function secondPassed() {
    var minutes = Math.round((seconds - 30)/60);
    var remainingSeconds = seconds % 60;
    if (remainingSeconds < 10) {
        remainingSeconds = "0" + remainingSeconds; 
    }
    document.getElementById('countdown').innerHTML = minutes + ":" + remainingSeconds;
    if (seconds == 0) {
        clearInterval(countdownTimer);
        document.getElementById('countdown').innerHTML = "Buzz Buzz";
        window.location = <?php echo("'" . $realReturn . "'") ?>; 
    } else {
        seconds--;
    }
}
 
var countdownTimer = setInterval('secondPassed()', 1000);
</script>
</head>
<body>
TEST: logged out ? <br>
<?php
require_once('/usr/share/simplesamlphp-1.11.0/lib/_autoload.php');

$state = SimpleSAML_Auth_State::loadState((string)$_REQUEST['LogoutState'], 'MyLogoutState');
$ls = $state['saml:sp:LogoutStatus']; /* Only works for SAML SP */
if ($ls['Code'] === 'urn:oasis:names:tc:SAML:2.0:status:Success' && !isset($ls['SubCode'])) {
    /* Successful logout. */
    echo($ls['Code'] . "<br>" . $ls['SubCode'] . "<br>");
    echo("You have been logged out.");
} else {
    /* Logout failed. Tell the user to close the browser. */
    echo($ls['Code'] . "<br>" . $ls['SubCode'] . "<br>");
    echo("We were unable to log you out of all your sessions.<br>To be completely sure that you are logged out, you need to close your web browser.");
}

?>
<hr>
You will be redirected to the startpage in
<span id="countdown" class="timer"></span>
</body>
</html>
