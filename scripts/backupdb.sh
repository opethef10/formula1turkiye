#!/bin/bash

# Configuration
HOME_FOLDER="$HOME"
F1T_FOLDER="$HOME_FOLDER/formula1turkiye.pythonanywhere.com/"
BACKUP_FOLDER="$HOME_FOLDER/.backups/"
BACKUP_FILE_PREFIX="f1t.db."
DB_EXTENSION=".sqlite3"
DB_FILE="$F1T_FOLDER/db$DB_EXTENSION"

# Ensure backup folder exists
mkdir -p "$BACKUP_FOLDER"

# Function to get modification time of a file (formatted)
get_file_mtime_formatted() {
    date -r "$1" +"%Y%m%d_%H%M%S"
}

# Function to get modification time of a file (epoch timestamp)
get_file_mtime_epoch() {
    date -r "$1" +"%s"
}

# Find the latest backup file
latest_backup=$(ls -1 "$BACKUP_FOLDER" | grep "$BACKUP_FILE_PREFIX" | grep ".gz" | tail -n 1)

# Check if the database needs to be backed up
should_copy=true
db_mtime_epoch=$(get_file_mtime_epoch "$DB_FILE")

if [[ -n "$latest_backup" ]]; then
    latest_backup_file="$BACKUP_FOLDER/$latest_backup"
    backup_mtime_epoch=$(get_file_mtime_epoch "$latest_backup_file")

    if [[ "$db_mtime_epoch" -le "$backup_mtime_epoch" ]]; then
        should_copy=false
    fi
fi

# Backup and compress the database
if $should_copy; then
    # Use the database's last modified timestamp as the backup name
    DATETIME_FORMAT=$(get_file_mtime_formatted "$DB_FILE")
    BACKUP_FILE="$BACKUP_FOLDER/$BACKUP_FILE_PREFIX$DATETIME_FORMAT$DB_EXTENSION"

    echo "Creating a vacuumed backup..."

    # Step 1: Perform VACUUM INTO to create the backup
    sqlite3 "$DB_FILE" "VACUUM INTO '$BACKUP_FILE'"

    # Step 2: Compress the backup file using gzip
    gzip "$BACKUP_FILE"
    echo "Backup successfully created and compressed: $BACKUP_FILE.gz"
else
    echo "No need to update the backup, as the database has not been modified."
fi
