import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DATABASE_PATH = Path("data/cylens_backup.db")
BACKUP_DIRECTORY = Path("data/backups")

def create_database_backup():
    """Create a consistent SQLite backup using the online backup API."""

    BACKUP_DIRECTORY.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIRECTORY / f"cylens_backup_{timestamp}.db"

    source_connection = None
    backup_connection = None

    try:
        source_connection = sqlite3.connect(DATABASE_PATH)
        backup_connection = sqlite3.connect(backup_path)

        source_connection.backup(backup_connection)

        result = backup_connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        if result != "ok":
            raise RuntimeError(
                f'Backup integrity check failed: {result}'
            )
        print(f"Database backup created: {backup_path}")

        cleanup_old_backups(keep=7)

        return backup_path

    except Exception:
        if backup_path.exists():
            backup_path.unlink()
        raise
    finally:
        if backup_connection:
            backup_connection.close()

        if source_connection:
            source_connection.close()


def cleanup_old_backups(keep=7):
    """Keep the newest valid backups and remove older backup files."""

    BACKUP_DIRECTORY.mkdir(parents=True, exist_ok=True)

    backup_files = sorted(
        BACKUP_DIRECTORY.glob("cylens_backup_*.db"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    valid_backups = []

    for backup_path in backup_files:
        connection = None

        try:
            connection = sqlite3.connect(backup_path)

            result = connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]

            if result == "ok":
                valid_backups.append(backup_path)
            else:
                print(f"Invalid backup detected: {backup_path}")

        except sqlite3.Error as error:
            print(f"Could not validate {backup_path}: {error}")

        finally:
            if connection:
                connection.close()

    # Remove older valid backups only after checking all files.
    for old_backup in valid_backups[keep:]:
        old_backup.unlink()
        print(f"Old backup removed: {old_backup}")

    print(f"Valid backups retained: {min(len(valid_backups), keep)}")
