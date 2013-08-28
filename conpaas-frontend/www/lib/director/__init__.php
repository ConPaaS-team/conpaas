<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */


require_module('https');


class Director {

    private static $version = "";

    public static function getVersion() {
        if (self::$version == "") {
            self::$version = HTTPS::get(Conf::DIRECTOR . '/version');
        }
        return self::$version;
    }

}


?>

