<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */


require_module('https');


class Director {

    private static $version = "";
    private static $support_external_idp = "-";

    public static function getVersion() {
        if (self::$version == "") {
            self::$version = HTTPS::get(Conf::DIRECTOR . '/version');
        }
        return self::$version;
    }

    public static function getSupportExternalIdp() {
        if (self::$support_external_idp == "-") {
            self::$support_external_idp = HTTPS::get(Conf::DIRECTOR . '/support_external_idp');
            // user_error('support_external_idp = ' . self::$support_external_idp);
            if ( strtolower(self::$support_external_idp) == 'true' ) {
                self::$support_external_idp = true;
            } else {
                self::$support_external_idp = false;
            }
        }
        return self::$support_external_idp;
    }

}


?>

