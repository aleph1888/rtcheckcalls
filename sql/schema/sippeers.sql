#
# Table structure for table `sippeers`
#

DROP TABLE IF EXISTS sippeers;
CREATE TABLE IF NOT EXISTS `sippeers` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `name` varchar(32) NOT NULL,
      `regseconds` int(11) DEFAULT NULL,
      `useragent` varchar(128) DEFAULT NULL,
      `lastms` int(11) DEFAULT NULL,
      `host` varchar(40) DEFAULT NULL,
      `ipaddr` varchar(45) DEFAULT NULL,
      `port` int(5) DEFAULT NULL,
      `type` enum('friend','user','peer') DEFAULT NULL,
      `context` varchar(40) DEFAULT NULL,
      `secret` varchar(40) DEFAULT NULL,
      `md5secret` varchar(40) DEFAULT NULL,
      `transport` varchar(40) DEFAULT NULL,
      `directmedia` enum('yes','no','nonat','update') DEFAULT NULL,
      `nat` enum('yes','no','never','route') DEFAULT NULL,
      `language` varchar(40) DEFAULT NULL,
      `disallow` varchar(40) DEFAULT NULL,
      `allow` varchar(40) DEFAULT NULL,
      `mailbox` varchar(40) DEFAULT NULL,
      `regexten` varchar(40) DEFAULT NULL,
      `qualify` varchar(40) DEFAULT NULL,
      `hasvoicemail` enum('yes','no') DEFAULT NULL,
      `encryption` enum('yes','no') DEFAULT NULL,
      `avpf` enum('yes','no') DEFAULT NULL,
      `directrtpsetup` enum('yes','no') DEFAULT NULL,
      `icesupport` enum('yes','no') DEFAULT NULL,
     `callbackextension` varchar(40) DEFAULT NULL,
     `sippasswd` varchar(80) DEFAULT NULL,
     `insecure` varchar(40) DEFAULT NULL,
     `defaultuser` varchar(40) DEFAULT NULL,
     `regserver` varchar(40) DEFAULT NULL,
     `fullcontact` varchar(256) DEFAULT NULL,
     `callerid` varchar(80) DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `name` (`name`),
      KEY `ipaddr` (`ipaddr`,`port`),
      KEY `host` (`host`,`port`)
) ENGINE=MyISAM;

