import sqlite3
import csv
from datetime import datetime, timezone

conn = sqlite3.connect("lobby_events.sqlite")
cur = conn.cursor()

cur.execute("""
    SELECT id, zone, start_ms, duration_ms, severity, incident_ref 
    FROM incidents 
    WHERE start_ms BETWEEN 1782902400000 AND 1782902650000
    ORDER BY start_ms, id
""")
rows = cur.fetchall()
print(f"Incidents in window ({len(rows)}):")
for r in rows:
    dt = datetime.fromtimestamp(r[2]/1000.0, tz=timezone.utc)
    print(f"ID={r[0]}, Zone={r[1]}, start_ms={r[2]}, dur={r[3]}, sev={r[4]}, ref={r[5]}, dt={dt.strftime('%Y-%m-%d %H:%M:%S.%f %a')}")

# Also check timestamps across the entire database to see the date range and patterns
cur.execute("SELECT MIN(start_ms), MAX(start_ms), COUNT(*) FROM incidents")
min_t, max_t, cnt = cur.fetchone()
print(f"\nDB range: min={min_t} ({datetime.fromtimestamp(min_t/1000, tz=timezone.utc)}), max={max_t} ({datetime.fromtimestamp(max_t/1000, tz=timezone.utc)}), count={cnt}")
