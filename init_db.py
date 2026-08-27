from database import get_connection

def initialize_database():
    """Create the CyLens database and its tables."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            threat_type TEXT NOT NULL,
            severity TEXT,
            source_ip TEXT,
            source_country TEXT,
            target_ip TEXT,
            target_country TEXT,
            description TEXT,
            data_source TEXT,
            confidence_score INTEGER,
            raw_data TEXT
        )
        """
    )

    connection.commit()
    connection.close()

    print("CyLens database initialized successfully.")

if __name__ == "__main__":
    initialize_database()