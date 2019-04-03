## RUN
```bash
docker build -t kaicoin .
docker tag kaicoin ccr.ccs.tencentyun.com/360ctf/kaicoin
docker run -it --rm --name kaicoin -p 5000:5000 kaicoin
```

## PoC

flag{acf7ef943fdeb3cbfed8dd0d8f584731}