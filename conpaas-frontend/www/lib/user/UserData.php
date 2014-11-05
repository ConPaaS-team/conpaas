<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('https');
require_module('logging');

class UserData {
    public static function createUser($username, $email, $fname, $lname,
    		$affiliation, $passwd, $credit, $uuid, $openid) {

        $data = array(
            'username'    => $username, 
            'email'       => $email,
            'fname'       => $fname,
            'lname'       => $lname,
            'affiliation' => $affiliation,
            'password'    => $passwd,
            'credit'      => $credit,
            'openid'      => $openid,
            'uuid'        => $uuid);

        $res = json_decode(HTTPS::post(Conf::DIRECTOR . '/new_user', $data));

        if (property_exists($res, 'msg')) {
            throw new Exception($res->msg);
        }

    	return $res->uid;
    }

    public static function getUserByOpenid($openid, $refresh_certs=false) {
       $res = HTTPS::post(Conf::DIRECTOR . '/login', array('openid' => $openid 
           /* 'password' => (isset($_SESSION['password']) ? $_SESSION['password'] : 'avoid "Undefined index: password" message')  */
           ));

       user_error('getUserByOpenid: HTTPS on director /login with openid = <' . $openid . '> returns ' . $res, E_USER_NOTICE);
       return self::set_up_user(null, $res, $refresh_certs);
    }

    public static function getUserByUuid($uuid, $refresh_certs=false) {
       $res = HTTPS::post(Conf::DIRECTOR . '/login', array('uuid' => $uuid 
           /* 'password' => (isset($_SESSION['password']) ? $_SESSION['password'] : 'avoid "Undefined index: password" message')  */
           ));

       user_error('getUserByUuid: HTTPS on director /login with uuid = <' . $uuid . '> returns ' . $res, E_USER_NOTICE);
       return self::set_up_user(null, $res, $refresh_certs);
    }

    public static function getUserByName($username, $refresh_certs=false) {
       $res = HTTPS::post(Conf::DIRECTOR . '/login', array('username' => $username, 
           'password' => (isset($_SESSION['password']) ? $_SESSION['password'] : 'avoid "Undefined index: password" message')));

       user_error('getUserByName: HTTPS on director /login with username = <' . $username . '> returns ' . $res, E_USER_NOTICE);
       return self::set_up_user($username, $res, $refresh_certs);
    }

    private static function set_up_user($username, $res, $refresh_certs) {

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
                           'affiliation' => $user->affiliation,
                           'openid' => $user->openid,
                           'uuid' => $user->uuid);

       $uid = $user->uid;

       $cert_file = sys_get_temp_dir(). "/$uid/cert.pem";

       if (is_file($cert_file) && !$refresh_certs) {
           return $user_array;
       }

       /* Get and save user certificates zip file */
       if (isset($_SESSION['password'])) {
           $res = HTTPS::post(Conf::DIRECTOR . '/getcerts',
               array('username' => $username, 'password' => $_SESSION['password']));
       } elseif (isset($_SESSION['uuid'])) {
           $res = HTTPS::post(Conf::DIRECTOR . '/getcerts',
               array('username' => $username, 'uuid' => $_SESSION['uuid']));
       } elseif (isset($_SESSION['openid'])) {
           $res = HTTPS::post(Conf::DIRECTOR . '/getcerts',
               array('username' => $username, 'openid' => $_SESSION['openid']));
       }

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
