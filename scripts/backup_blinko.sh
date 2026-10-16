#!/bin/bash

set -euxo pipefail
IFS=$'\n\t'

CONTAINER_NAME=database
CONTAINER_NS=blinko
DB_ROOT_PASSWORD=${BLINKO_POSTGRES_PASSWORD} # replace with static when installing as cronjob
RETENTION_DAYS=30

backup_dir="/backup/${CONTAINER_NS}"
container_id=$(docker service ps ${CONTAINER_NS}_${CONTAINER_NAME} --quiet | head -n1)
now=$(date +"%Y%m%d-%H%M%S")

mkdir -p "$backup_dir"
cd "$backup_dir"

# Backup Database
docker exec ${CONTAINER_NS}_${CONTAINER_NAME}.1.${container_id} \
    pg_dump -U blinko blinko > "${now}_${CONTAINER_NS}.sql"
gzip "${now}_${CONTAINER_NS}.sql"

# Backup Volumes
tar -czf "${now}_${CONTAINER_NS}.tar.gz" -C "/var/lib/docker/volumes/blinko_app/_data/" .

# Cleanup old backups
ls -t | grep tar.gz | sed -e "1,${RETENTION_DAYS}d" | xargs -r -d '\n' rm
ls -t | grep sql.gz | sed -e "1,${RETENTION_DAYS}d" | xargs -r -d '\n' rm
