
## RUN
```bash
docker build -t xss1 .
docker tag xss1 ccr.ccs.tencentyun.com/360ctf/xss1
docker run -it --rm -p 5000:5000 --name xss1 xss1
```

## PoC

flag{41064c3f5d42abbe4a8871cb08deb880}