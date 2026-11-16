import sqlite3
from pathlib import Path

DATABASE_PATH = Path("data/cylens_backup.db")

def get_connection():
    """Create and return a connection to the CyLens database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection