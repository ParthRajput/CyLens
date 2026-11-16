import os

import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

from database import get_connection

load_dotenv()


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
    """Add a threat or record changes in its intelligence history."""

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT id, confidence_score, severity, description
            FROM threats
            WHERE source_ip = ?
            AND threat_type = ?
            AND data_source = ?
            """,
            (source_ip, threat_type, data_source),
        )

        existing_threat = cursor.fetchone()

        if existing_threat is None:
            cursor.execute(
                """
                INSERT INTO threats (
                    timestamp, threat_type, severity,
                    source_ip, source_country, description,
                    data_source, confidence_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp, threat_type, severity,
                    source_ip, source_country, description,
                    data_source, confidence_score,
                ),
            )

            threat_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO threat_history (
                    threat_id, timestamp, confidence_score,
                    severity, description
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    threat_id, timestamp, confidence_score,
                    severity, description,
                ),
            )

            connection.commit()
            print(f"New threat added: {source_ip}")
            return True

        threat_id = existing_threat["id"]

        changed = (
            existing_threat["confidence_score"] != confidence_score
            or existing_threat["severity"] != severity
            or existing_threat["description"] != description
        )

        if changed:
            cursor.execute(
                """
                UPDATE threats
                SET timestamp = ?,
                    severity = ?,
                    source_country = ?,
                    description = ?,
                    confidence_score = ?
                WHERE id = ?
                """,
                (
                    timestamp, severity, source_country,
                    description, confidence_score, threat_id,
                ),
            )

            cursor.execute(
                """
                INSERT INTO threat_history (
                    threat_id, timestamp, confidence_score,
                    severity, description
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    threat_id, timestamp, confidence_score,
                    severity, description,
                ),
            )

            connection.commit()
            print(f"Threat intelligence updated: {source_ip}")
            return True

        print(f"No intelligence changes: {source_ip}")
        return False

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_all_threats():
    """Retrieve all threat records from the CyLens database."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM threats")

    threats = cursor.fetchall()

    connection.close()

    return threats


def check_ip_abuse(ip_address):
    """
    Check an IP address using the AbuseIPDB API.

    Returns:
        dict: Normalised threat intelligence data.
    """

    api_key = os.getenv("ABUSEIPDB_API_KEY")

    if not api_key:
        raise RuntimeError("ABUSEIPDB_API_KEY was not found in .env")

    response = requests.get(
        "https://api.abuseipdb.com/api/v2/check",
        headers={
            "Accept": "application/json",
            "Key": api_key,
        },
        params={
            "ipAddress": ip_address,
            "maxAgeInDays": 90,
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()["data"]

    return {
        "source_ip": data.get("ipAddress"),
        "source_country": data.get("countryCode"),
        "confidence_score": data.get("abuseConfidenceScore"),
        "description": (
            f"AbuseIPDB reports: {data.get('totalReports', 0)}. "
            f"Abuse confidence score: "
            f"{data.get('abuseConfidenceScore', 0)}."
        ),
        "data_source": "AbuseIPDB",
    }

def fetch_abuseipdb_blacklist():
    """Fetch a small sample of high-confidence IPs from AbuseIPDB."""

    api_key = os.getenv("ABUSEIPDB_API_KEY")

    if not api_key:
        raise RuntimeError("ABUSEIPDB_API_KEY was not found in .env")

    response = requests.get(
        "https://api.abuseipdb.com/api/v2/blacklist",
        headers={
            "Accept": "application/json",
            "Key": api_key,
        },
        params={
            "confidenceMinimum": 90,
            "limit": 10,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("data", [])


def ingest_abuseipdb_blacklist():
    """Fetch and store AbuseIPDB blacklist indicators."""

    blacklist = fetch_abuseipdb_blacklist()

    processed = 0
    changed = 0

    for item in blacklist:
        ip_address = item.get("ipAddress")

        if not ip_address:
            continue

        confidence_score = int(item.get("abuseConfidenceScore", 0))

        # Derive severity from confidence score.
        if confidence_score >= 90:
            severity = "Critical"
        elif confidence_score >= 70:
            severity = "High"
        elif confidence_score >= 40:
            severity = "Medium"
        else:
            severity = "Low"

        timestamp = datetime.now(timezone.utc).isoformat()
        last_reported = item.get("lastReportedAt", "Unknown")

        description = (
            f"AbuseIPDB blacklist indicator. "
            f"Confidence score: {confidence_score}%. "
            f"Last reported: {last_reported}."
        )

        result = add_threat(
            timestamp=timestamp,
            threat_type="IP Reputation",
            severity=severity,
            source_ip=ip_address,
            source_country=item.get("countryCode"),
            description=description,
            data_source="AbuseIPDB",
            confidence_score=confidence_score,
        )

        processed += 1

        if result:
            changed += 1

    print("\nAbuseIPDB ingestion completed.")
    print(f"Indicators processed: {processed}")
    print(f"New or updated indicators: {changed}")
    print(f"Unchanged indicators: {processed - changed}")

    return {
        "processed": processed,
        "changed": changed,
        "unchanged": processed - changed,
    }
