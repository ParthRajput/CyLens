from services.threat_services import fetch_abuseipdb_blacklist

blacklist = fetch_abuseipdb_blacklist()

print(f"Total IPs retrieved: {len(blacklist)}")

for ip in blacklist:
    print(
        f"IP: {ip.get('ipAddress')} | "
        f"Country: {ip.get('countryCode')} | "
        f"Confidence: {ip.get('abuseConfidenceScore')}%"
    )

print("\nFUll first record:")
print(blacklist[0])