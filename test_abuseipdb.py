from datetime import datetime

from services.threat_services import check_ip_abuse, add_threat

result = check_ip_abuse("8.8.8.8")

add_threat(
    timestamp=datetime.now().isoformat(),
    threat_type="IP Reputation",
    severity="Low",
    source_ip=result["source_ip"],
    source_country=result["source_country"],
    description=result["description"],
    data_source=result["data_source"],
    confidence_score=result["confidence_score"],
)
print("Threat successfully added to CyLens database")