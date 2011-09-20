<?php 

session_set_cookie_params(60 * 60 * 24 * 15); // expires in 15 days
session_start();

class Conf {
	
	// These configuration options are deprecated 
	// and should not be used any more.
	// const MYSQL_HOST = '';
	// const MYSQL_USER = '';
	// const MYSQL_PASS = '';
	// const MYSQL_DB = '';

	// This variable must be set to the directory where
	// configuration files are located. Beware: it is highly
	// recommended to keep configuration files *out* of the 
	// Web server's document directory.
	const CONF_DIR = '/etc/conpaas';
}

?>