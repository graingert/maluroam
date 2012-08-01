-- phpMyAdmin SQL Dump
-- version 3.4.10.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: May 02, 2012 at 09:07 AM
-- Server version: 5.1.61
-- PHP Version: 5.3.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `3yp_platform`
--

-- --------------------------------------------------------

--
-- Table structure for table `blacklists`
--

CREATE TABLE IF NOT EXISTS `blacklists` (
  `bl_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `serialized` longtext NOT NULL,
  `updated` datetime NOT NULL,
  `hide` tinyint(1) NOT NULL,
  PRIMARY KEY (`bl_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

--
-- Table structure for table `event`
--

CREATE TABLE IF NOT EXISTS `event` (
  `event_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `radius_account_id` varchar(255) NOT NULL,
  `radius_session_id` varchar(255) NOT NULL,
  `radius_info` text NOT NULL,
  `ip_src` varchar(255) NOT NULL,
  `ip_dst` varchar(255) NOT NULL,
  `start` datetime NOT NULL,
  `finish` datetime NOT NULL,
  `alerts` bigint(20) NOT NULL,
  `blacklist` int(11) NOT NULL,
  `rule` bigint(20) NOT NULL,
  `rule_class` varchar(31) NOT NULL,
  PRIMARY KEY (`event_id`),
  UNIQUE KEY `username` (`username`,`ip_src`,`ip_dst`,`start`,`finish`),
  KEY `user` (`username`),
  KEY `ip_dest` (`ip_dst`),
  KEY `ip_src` (`ip_src`),
  KEY `blacklist` (`blacklist`),
  KEY `alert_id` (`rule`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5192 ;

-- --------------------------------------------------------

--
-- Table structure for table `rules`
--

CREATE TABLE IF NOT EXISTS `rules` (
  `rule_id` bigint(20) NOT NULL,
  `rule_name` varchar(255) NOT NULL,
  `hide` tinyint(1) NOT NULL,
  PRIMARY KEY (`rule_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `scripts`
--

CREATE TABLE IF NOT EXISTS `scripts` (
  `script_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `lastupdated` datetime NOT NULL,
  PRIMARY KEY (`script_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
