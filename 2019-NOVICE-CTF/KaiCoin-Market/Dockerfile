FROM mysql:5.7

COPY web4market /web4market
WORKDIR /web4market

RUN set -ex \
    # temp disabled
    && sed -i '/security.debian.org/d' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y python3 python3-pip gcc zlib1g-dev libjpeg-dev libpng-dev libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install -r requirements.txt

ENV MYSQL_DATABASE=market MYSQL_USER=user MYSQL_PASSWORD=u5erp4ssword MYSQL_RANDOM_ROOT_PASSWORD=yes
COPY init.sql /docker-entrypoint-initdb.d/

COPY web4market-entrypoint.sh /
RUN chmod a+x /web4market-entrypoint.sh

# hack
# RUN sed -i "s/_charsets.add(Charset(247.*/_charsets.add(Charset(255, 'utf8mb4', 'utf8mb4_unicode_ci', ''))/" /usr/local/lib/python3.4/dist-packages/pymysql/charset.py

EXPOSE 5000

ENTRYPOINT ["/web4market-entrypoint.sh"]
CMD ["python3", "run.py"]