import sqlite3
from datetime import datetime, timezone

conn = sqlite3.connect("lobby_events.sqlite")
cur = conn.cursor()

cur.execute("SELECT id, zone, start_ms, duration_ms, severity, incident_ref FROM incidents WHERE severity = 5")
rows = cur.fetchall()
print(f"Total sev 5 rows: {len(rows)}")
for r in rows:
    dt = datetime.fromtimestamp(r[2]/1000.0, tz=timezone.utc)
    print(f"ID={r[0]}, Zone={r[1]}, start_ms={r[2]}, dur={r[3]}, sev={r[4]}, ref={r[5]}, dt={dt.strftime('%Y-%m-%d %H:%M:%S.%f %a')}")

cur.execute("SELECT severity, count(*) FROM incidents GROUP BY severity")
print("\nSeverity breakdown:")
for r in cur.fetchall():
    print(f"Severity {r[0]}: {r[1]} incidents")
