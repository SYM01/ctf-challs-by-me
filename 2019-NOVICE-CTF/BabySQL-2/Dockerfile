FROM mysql:latest

RUN set -ex; \
    apt-get update; \
    apt-get install -y python3 python3-pip; \
    rm -rf /var/lib/apt/lists/*;

COPY init.sql /docker-entrypoint-initdb.d/
COPY src /app/
WORKDIR /app/

RUN pip3 install -r requirements.txt

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

EXPOSE 5000

COPY entrypoint-app.sh /
ENV MYSQL_ROOT_PASSWORD root
ENTRYPOINT /entrypoint-app.sh
