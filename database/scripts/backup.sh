#!/bin/bash
# database/scripts/backup.sh
# Backup MongoDB database to a timestamped dump

BACKUP_DIR="/backups/twinflow"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="${BACKUP_DIR}/twinflow_${TIMESTAMP}"

mkdir -p $BACKUP_DIR

echo "Starting backup to $BACKUP_PATH"

mongodump --uri="$MONGO_URI" --out="$BACKUP_PATH"

if [ $? -eq 0 ]; then
    echo "Backup successful."
    # Optionally compress
    tar -czf "${BACKUP_PATH}.tar.gz" -C "$BACKUP_DIR" "$(basename $BACKUP_PATH)"
    rm -rf "$BACKUP_PATH"
    echo "Backup compressed: ${BACKUP_PATH}.tar.gz"
else
    echo "Backup failed."
    exit 1
fi