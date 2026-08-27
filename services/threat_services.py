from database import get_connection

def add_threat(
        timestamp,
        threat_type,
        severity,
        source_ip,
        source_country,
        description,
        data_source,
        confidence_score,
):
    """Add a new threat record to the database."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO threats (
            timestamp,
            threat_type,
            severity,
            source_ip,
            source_country,
            description,
            data_source,
            confidence_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                threat_type,
                severity,
                source_ip,
                source_country,
                description,
                data_source,
                confidence_score,
            ),
    )

def get_all_threats():
    """Retrieve all threat records from the CyLens database."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM threats")

    threats = cursor.fetchall()

    connection.close()

    return threats

    connection.commit()
    connection.close()