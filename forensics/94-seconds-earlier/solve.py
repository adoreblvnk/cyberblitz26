import sqlite3
import csv
from datetime import datetime

# Post-it note 1:
# Lobby controller clock is FAST.
# 17342 ms ahead of our desk DB.
# Facilities told. Still not fixed.

# Post-it note 2:
# Outage drill Wed: log it as sev 5

# Sensor CSV: controller timestamps
# Controller is FAST by 17342 ms ahead of desk DB.
# So desk_db_ms = controller_ms - 17342 ms.
# Or if desk DB is behind, controller = desk + 17342, so desk = controller - 17342.
# Wait, let's also check if desk DB was fast or controller was fast, or vice versa (+/- 17342).

conn = sqlite3.connect("lobby_events.sqlite")
cur = conn.cursor()

print("--- All incidents with duration_ms = 94000 ---")
cur.execute("SELECT id, zone, start_ms, duration_ms, severity, incident_ref FROM incidents WHERE duration_ms = 94000")
rows = cur.fetchall()
print(f"Total rows with duration 94000: {len(rows)}")

# Let's inspect sensor_window.csv outages
outages = {}
with open("sensor_window.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        t = int(row["controller_ms"])
        zone = row["zone"]
        evt = row["event"]
        if evt == "lux-loss":
            outages[zone] = {"start": t}
        elif evt == "lux-restored":
            if zone in outages:
                outages[zone]["end"] = t
                outages[zone]["dur"] = t - outages[zone]["start"]

print("\n--- Outages in sensor_window.csv ---")
for zone, data in outages.items():
    print(f"Zone: {zone}, start: {data['start']}, end: {data.get('end')}, dur: {data.get('dur')}")

print("\n--- Checking matches with offset +/- 17342 ms ---")
OFFSET = 17342
for zone, data in outages.items():
    if data.get("dur") == 94000:
        ctrl_start = data["start"]
        # If controller is 17342 ahead of desk DB:
        desk_start_expected = ctrl_start - OFFSET
        desk_start_alt = ctrl_start + OFFSET
        print(f"\nZone {zone} (dur 94s): ctrl_start={ctrl_start}")
        print(f"  Expecting desk_start = {desk_start_expected} (or alt {desk_start_alt})")
        
        cur.execute("SELECT * FROM incidents WHERE zone = ?", (zone,))
        zone_incidents = cur.fetchall()
        for inc in zone_incidents:
            diff1 = inc[2] - desk_start_expected
            diff2 = inc[2] - desk_start_alt
            diff_raw = inc[2] - ctrl_start
            if abs(diff1) < 5000 or abs(diff2) < 5000 or abs(diff_raw) < 5000:
                print(f"  Candidate: {inc}, diff1={diff1}, diff2={diff2}, diff_raw={diff_raw}")

print("\n--- Checking all incidents for close matches to any expected start ---")
for inc in rows:
    for zone, data in outages.items():
        if data.get("dur") == 94000:
            ctrl_start = data["start"]
            diff = inc[2] - (ctrl_start - OFFSET)
            if abs(diff) < 20000:
                print(f"Close incident: {inc}, zone={zone}, diff={diff}")
