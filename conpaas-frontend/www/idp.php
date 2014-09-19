<?php
#  TODO  cleanup code
require_once('__init__.php');
require_module('ui/page');
require_module('director');
$data = array();

if (isset($_POST['source'])) {
    $data['source'] = $_POST['source'];
    $success =  true;
    $sucstr = "true";
} else {
    $success = false;
    $sucstr = "false";
}
#$page = new Page;
#echo HTTPS::post(Conf::DIRECTOR . '/ipdlogin', $data);
$content = HTTPS::post(Conf::DIRECTOR . '/idplogin', $data);
user_error("Success = " . $sucstr);
user_error("Content = " . $content);
if ($success) {
    # echo "Hallo<br> ";
    $targetURL="success.php";
    # echo $content;
    # echo "<hr>";
    $lines = array();
    $lines = explode( "\n", $content );
    foreach ($lines as $l) {
        if (preg_match("/href=/", $l))
        break;
    }
    $arr = explode( '"', $l );
    $targetURL = $arr[1];
    # echo $targetURL;
    user_error("targetURL = " . $targetURL);
    echo '<META HTTP-EQUIV="Refresh" Content="0; URL=' . $targetURL . '">';    
    # exit;
} else {
    # $targetURL = "idp.php" ;
    # echo '<META HTTP-EQUIV="Refresh" Content="0; URL=' . $targetURL . '">';    
    echo $content;
}
?>
