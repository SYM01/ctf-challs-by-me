#!/bin/bash

set -e

if [ "${1:0:1}" = '-' ]; then
	set -- python3 run.py "$@"
fi

docker-entrypoint.sh --character-set-server=utf8mb4 --collation-server=utf8mb4_general_ci &
exec "$@"