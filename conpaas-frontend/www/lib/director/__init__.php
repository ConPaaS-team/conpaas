<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */


require_module('https');


class Director {

    private static $version = "";
    private static $support_external_idp = "-";
    private static $support_openid = "-";

    public static function getVersion() {
        if (self::$version == "") {
            self::$version = HTTPS::get(Conf::DIRECTOR . '/version');
        }
        return self::$version;
    }

    public static function getSupportExternalIdp() {
        if (self::$support_external_idp == "-") {
            self::$support_external_idp = HTTPS::get(Conf::DIRECTOR . '/support_external_idp');
            user_error('support_external_idp = ' . self::$support_external_idp);
            if ( strtolower(self::$support_external_idp) == 'true' ) {
                self::$support_external_idp = true;
            } else {
                self::$support_external_idp = false;
            }
        }
        return self::$support_external_idp;
    }

    public static function getSupportOpenID() {
        if (self::$support_openid == "-") {
            self::$support_openid = HTTPS::get(Conf::DIRECTOR . '/support_openid');
            user_error('support_openid = ' . self::$support_openid);
            if ( strtolower(self::$support_openid) == 'true' ) {
                self::$support_openid = true;
            } else {
                self::$support_openid = false;
            }
        }
        return self::$support_openid;
    }

}


?>

