#!/bin/bash


run() {
    gosu www-data twistd -n web --port "tcp:port=8090" --wsgi blog.app
}

echo "$@"
# run mysqld
docker-entrypoint.sh mysqld &

if [ -e "$@" ]; then
    run
else
    exec "$@"
fi
