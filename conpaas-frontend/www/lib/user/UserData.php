<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

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
