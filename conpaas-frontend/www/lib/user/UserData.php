<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('https');
require_module('logging');

class UserData {
    public static function createUser($username, $email, $fname, $lname,
    		$affiliation, $passwd, $credit) {

        $data = array(
            'username'    => $username, 
            'email'       => $email,
            'fname'       => $fname,
            'lname'       => $lname,
            'affiliation' => $affiliation,
            'password'    => $passwd,
            'credit'      => $credit);

        $res = json_decode(HTTPS::post(Conf::DIRECTOR . '/new_user', $data));

        if (property_exists($res, 'msg')) {
            throw new Exception($res->msg);
        }

    	return $res->uid;
    }

	public static function getUserByName($username, $refresh_certs=false) {
       $res = HTTPS::post(Conf::DIRECTOR . '/login', array('username' => $username, 
           'password' => (isset($_SESSION['password']) ? $_SESSION['password'] : 'avoid "Undefined index: password" message')));

       $user = json_decode($res);

       if (!$user) {
           /* Authentication failed */
           return false;
       }

       $user_array = array('uid' => $user->uid, 
                           'username' => $user->username,
                           'passwd' => $user->password, 
                           'credit' => $user->credit,
                           'fname' => $user->fname,
                           'lname' => $user->lname,
                           'email' => $user->email,
                           'affiliation' => $user->affiliation);

       $uid = $user->uid;

       $cert_file = sys_get_temp_dir(). "/$uid/cert.pem";

       if (is_file($cert_file) && !$refresh_certs) {
           return $user_array;
       }

       /* Get and save user certificates zip file */
       $res = HTTPS::post(Conf::DIRECTOR . '/getcerts',
           array('username' => $username, 'password' => $_SESSION['password']));

       $zip_filename = sys_get_temp_dir() . "/conpaas_cert_$uid.zip";
       file_put_contents($zip_filename, $res);

       /* extract user's certificate */
       $zip = new ZipArchive;
       if ($zip->open($zip_filename) === TRUE) {
           /* create dest dir */
           $destdir = sys_get_temp_dir(). "/$uid";
           if (!is_dir($destdir)) {
               mkdir($destdir, 0777, true);
           }

           /* extract certs */
           $zip->extractTo($destdir);
           $zip->close();
       }

       return $user_array;
	}
}
?>
