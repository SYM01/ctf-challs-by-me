create schema baby;
create user baby@'%' identified by 'baby@360';
create user baby@127.0.0.1 identified by 'baby@360';
grant select on baby.* to baby@'%';
grant select on baby.* to baby@127.0.0.1;
flush privileges;

use baby;
create table flag (
    `flag` varchar(64) primary key
);

create table slogan (
    `id` int auto_increment primary key,
    `text` varchar(256)
);

insert into slogan (text) values 
    ('金钱可以解决99%的问题，剩下的1%可以用更多的金钱解决。'),
    ('努力不一定成功，但是不努力会好轻松。'),
    ('猫狗见面不是吻就是舔，人见面不是骗就是演。'),
    ('转角一般不会遇到爱，只会遇到乞丐。'),
    ('世上无难事只怕有钱人。'),
    ('难受的时候摸摸自己的胸，告诉自己是汉子，要坚强。'),
    ('物以类聚人以穷分。'),
    ('梦想还是要有的，不然喝多了你跟别人聊啥。'),
    ('万事开头难，中间难，最后更难。');


insert into flag values ('flag{281c824468eb40e6cbae1000d6b5f1e3}');