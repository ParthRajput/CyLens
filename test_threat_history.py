from services.threat_services import add_threat
from database import get_connection
from datetime import datetime, timezone

timestamp = datetime.now(timezone.utc).isoformat()

#Test 1: Insert a new threat
add_threat(
    timestamp,
    "IP Reputation",
    "Low",
    "192.0.2.10",
    "US",
    "Initial test reputation score: 10",
    "Test Source",
    10,
)

#Test 2: Update its reputation
add_threat(
    datetime.now(timezone.utc).isoformat(),
    "IP Reputation",
    "Medium",
    "192.0.2.10",
    "US",
    "Updated test reputation score: 50",
    "Test Source",
    50,
)

#Test 3: Submit unchanged intelligence
add_threat(
    datetime.now(timezone.utc).isoformat(),
    "IP Reputation",
    "Medium",
    "192.0.2.10",
    "US",
    "Updated test reputation score: 50",
    "Test Source",
    50,
)

#Verify database records
connection = get_connection()
cursor = connection.cursor()

cursor.execute("SELECT * FROM threats")
print("\nThreat records:", len(cursor.fetchall()))

cursor.execute("SELECT * FROM threat_history")
history = cursor.fetchall()

print("History snapshots:", len(history))

for record in history:
    print(dict(record))

connection.close()