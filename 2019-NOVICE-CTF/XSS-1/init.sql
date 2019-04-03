create schema xss;
create user xss@'%' identified by 'xss@360';
create user xss@127.0.0.1 identified by 'xss@360';
grant select,insert on xss.* to xss@'%';
grant select,insert on xss.* to xss@127.0.0.1;
flush privileges;

use xss;

create table `articles` (
    `uid` varchar(64) not null,
    `aid` int unsigned not null,
    `title` varchar(1024),
    `content` varchar(4096),
    primary key (`uid`, `aid` DESC)
);