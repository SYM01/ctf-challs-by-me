CREATE DATABASE  IF NOT EXISTS `0blog` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `0blog`;

DROP TABLE IF EXISTS `bl0g_articles`;
CREATE TABLE `bl0g_articles` (
  `aid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `uid` int(10) unsigned NOT NULL,
  `title` varchar(256) NOT NULL,
  `page_effect` varchar(70) NOT NULL,
  `content` text NOT NULL,
  PRIMARY KEY (`aid`),
  KEY `articles_uid_aid` (`uid`,`aid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `bl0g_comments`;
CREATE TABLE `bl0g_comments` (
  `cid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `aid` int(10) unsigned NOT NULL,
  `uid` int(10) unsigned NOT NULL,
  `comment` text NOT NULL,
  PRIMARY KEY (`cid`),
  KEY `comments_aid_cid` (`aid`,`cid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `bl0g_sessions`;
CREATE TABLE `bl0g_sessions` (
  `sid` char(84) NOT NULL,
  `expires` int(10) unsigned NOT NULL,
  `data` json NOT NULL,
  PRIMARY KEY (`sid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `bl0g_users`;
CREATE TABLE `bl0g_users` (
  `uid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(45) NOT NULL,
  `password` char(64) NOT NULL,
  `last_ip` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`uid`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE USER 'blog_user'@'127.0.0.1'
  IDENTIFIED BY '2887e91e2ea24a802e7baa328303ab42';

GRANT SELECT, INSERT, UPDATE, DELETE ON `0blog`.* TO 'blog_user'@'127.0.0.1';
