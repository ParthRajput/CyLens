from services.threat_services import ingest_abuseipdb_blacklist
if __name__ == "__main__":
    print("Starting Cylens threat intelligence collection...")

    try:
        result = ingest_abuseipdb_blacklist()

        print("\nCollection completed successfully.")
        print(result)

    except Exception as error:
        print(f"\nCollection failed: {error}")
        raise