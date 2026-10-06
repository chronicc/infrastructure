#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

BACKUP_DIR="/backup/kimai"
CONTAINER_NAME=db
CONTAINER_NS=kimai
DB_ROOT_PASSWORD=${KIMAI_DB_ROOT_PASSWORD} # replace with static when installing as cronjob
RETENTION_DAYS=30

container_id=$(docker service ps ${CONTAINER_NS}_${CONTAINER_NAME} --no-trunc | tail -n1 | awk '{print $1}')
now=$(date +"%Y%m%d-%H%M%S")

mkdir -p "$BACKUP_DIR"
cd "$BACKUP_DIR"

# Backup Database
docker exec ${CONTAINER_NS}_${CONTAINER_NAME}.1.${container_id} \
    mysqldump -u root --password=${DB_ROOT_PASSWORD} kimai > "${now}_${CONTAINER_NS}.sql"
gzip "${now}_${CONTAINER_NS}.sql"

# Backup Volumes
tar -czf "${now}_${CONTAINER_NS}.tar.gz" -C "/var/lib/docker/volumes/kimai_data/_data/" .

# Cleanup old backups
ls -t | grep tar.gz | sed -e "1,${RETENTION_DAYS}d" | xargs -d '\n' rm
ls -t | grep sql.gz | sed -e "1,${RETENTION_DAYS}d" | xargs -d '\n' rm
