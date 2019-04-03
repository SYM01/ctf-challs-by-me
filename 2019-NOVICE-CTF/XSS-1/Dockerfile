FROM mysql:latest

COPY google-chrome-stable_current_amd64.deb /tmp/
COPY chromedriver /usr/local/bin/

RUN dpkg -i /tmp/google-chrome-stable_current_amd64.deb; exit 0
RUN set -ex; \
    apt-get update; \
    apt-get install -y -f; \
    apt-get install -y python3 python3-pip; \
    rm -rf /var/lib/apt/lists/*; \
    rm -rf /tmp/*;

COPY init.sql /docker-entrypoint-initdb.d/
COPY src/requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt; 

COPY src /app/
WORKDIR /app/

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

EXPOSE 5000

COPY entrypoint-app.sh /
ENV MYSQL_ROOT_PASSWORD root
ENTRYPOINT /entrypoint-app.sh
