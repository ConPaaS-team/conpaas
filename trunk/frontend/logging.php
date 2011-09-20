<?php

function loadLoggingConfiguration() {
  $conf = parse_ini_file(Conf::CONF_DIR.'/log.ini', true);
  if ($conf === false) {
    throw new Exception('Could not read log configuration file db.ini');
  }
  return $conf['log'];
}

$logging_conf = loadLoggingConfiguration();
$logfile = fopen($logging_conf['file'], 'a');

function dlog($var) {
        global $logfile;
        fwrite($logfile, date('d-m-Y h:i:s').' '.print_r($var, true)."\n");
}

?>