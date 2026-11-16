from services.threat_services import ingest_abuseipdb_blacklist

result = ingest_abuseipdb_blacklist()

print("\nTest Result:")
print(result)