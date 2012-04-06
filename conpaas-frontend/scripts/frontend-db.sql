-- This script creates a database schema where the ConPaaS frontend
-- can store its state. Please update the first four lines to replace 
-- DB_USER, DB_PASSWD and DB_NAME with reasonable values. In particular,
-- make sure you replace DB_PASSWD with a strong password. You will need 
-- to enter these three values in the frontend/cond/db.ini file as well.

create user 'DB_USER'@'%' identified by 'DB_PASSWD';
create database DB_NAME;
grant all on DB_NAME.* to 'DB_USER'@'%';
use DB_NAME;


-- -------------------------------------------------------------------
-- Do not edit beyond this point unless you know what you are doing...
-- -------------------------------------------------------------------

CREATE TABLE `services` (
  `sid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(256) DEFAULT NULL,
  `type` varchar(32) DEFAULT NULL,
  `state` varchar(32) DEFAULT NULL,
  `creation_date` datetime DEFAULT NULL,
  `manager` varchar(512) DEFAULT NULL,
  `uid` int(11) DEFAULT NULL,
  `vmid` varchar(256) DEFAULT NULL,
  `cloud` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`sid`),
  KEY `searchbystate` (`state`),
  KEY `searchbyuser` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=latin1;

CREATE TABLE `users` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(256) DEFAULT NULL,
  `fname` varchar(256) DEFAULT NULL,
  `lname` varchar(256) DEFAULT NULL,
  `email` varchar(256) DEFAULT NULL,
  `affiliation` varchar(256) DEFAULT NULL,
  `passwd` varchar(256) DEFAULT NULL,
  `created` date DEFAULT NULL,
  `credit` int(11) DEFAULT '0',
  PRIMARY KEY (`uid`),
  KEY `searchname` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=latin1;
