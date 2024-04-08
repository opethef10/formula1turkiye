#!/usr/bin/env python

from datetime import datetime
from pathlib import Path
import shutil

NOW = datetime.now()
DATETIME_FORMAT = "%Y%m%d_%H%M%S"
HOME_FOLDER = Path.home()
F1T_FOLDER = HOME_FOLDER / "formula1turkiye.pythonanywhere.com/"
BACKUP_FOLDER = HOME_FOLDER / ".backups/"
BACKUP_FILE_PREFIX = "f1t.db."
DB_EXTENSION = ".sqlite3"
DB_FILE = F1T_FOLDER / f"db{DB_EXTENSION}"
DB_FILE_MODIFIED_DATETIME = datetime.fromtimestamp(DB_FILE.stat().st_mtime).replace(microsecond=0)


def get_latest_backup():
    backups = BACKUP_FOLDER.glob(f"{BACKUP_FILE_PREFIX}*{DB_EXTENSION}")
    return max(backups, default=None)

def should_copy():
    latest_backup_path = get_latest_backup()
    if latest_backup_path:
        latest_backup_datetime = datetime.strptime(latest_backup_path.stem[len(BACKUP_FILE_PREFIX):], DATETIME_FORMAT)
        return DB_FILE_MODIFIED_DATETIME > latest_backup_datetime
    else:
        return True

if __name__ == "__main__":
    if should_copy():
        BACKUP_FILE_DESTINATION = BACKUP_FOLDER / f"{BACKUP_FILE_PREFIX}{DB_FILE_MODIFIED_DATETIME:{DATETIME_FORMAT}}{DB_EXTENSION}"
        shutil.copy(DB_FILE, BACKUP_FILE_DESTINATION)
        print("Backup successfully created.")
    else:
        print("No need to update the backup, as the database has not been modified.")

