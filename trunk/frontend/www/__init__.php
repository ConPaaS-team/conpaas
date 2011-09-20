<?php 

session_set_cookie_params(60 * 60 * 24 * 15); // expires in 15 days
session_start();

class Conf {
	
	const MYSQL_HOST = 'localhost';
	const MYSQL_USER = 'conpaasweb';
	const MYSQL_PASS = 'exNsCFHEmh';
	const MYSQL_DB = 'conpaasweb';

	const CONF_DIR = '/home/claudiu/public_html/conf';
}

?>