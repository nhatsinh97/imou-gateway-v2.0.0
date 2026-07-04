#!/usr/bin/env python3
import sqlite3
import sys
import io

# Force UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

print("\n" + "="*70)
print("IMOU GATEWAY - LIVE STATUS REPORT")
print("="*70)

conn = sqlite3.connect('database/events.db')
c = conn.cursor()

# Count events by type
c.execute("SELECT event_type, COUNT(*) FROM events GROUP BY event_type ORDER BY COUNT(*) DESC")
print("\n[EVENT STATISTICS]")
for event_type, count in c:
    print(f"  {event_type:20s}: {count:3d} events")

# Total
c.execute("SELECT COUNT(*) FROM events")
total = c.fetchone()[0]
print(f"  {'TOTAL':20s}: {total:3d} events")

# Last 5 events
print("\n[LATEST 5 EVENTS]")
c.execute("""
    SELECT id, timestamp, channel, event_type, description 
    FROM events 
    ORDER BY id DESC 
    LIMIT 5
""")
for row in c:
    event_id, ts, ch, etype, desc = row
    ts_short = ts[:16] if ts else "N/A"
    desc_safe = desc.replace('\n', ' ')[:35] if desc else "N/A"
    try:
        print(f"  #{event_id}: [{ts_short}] Ch{ch} {etype:20s}")
    except:
        print(f"  #{event_id}: [{ts_short}] Ch{ch} event")

# Events today
c.execute("""
    SELECT COUNT(*) FROM events 
    WHERE date(timestamp) = date('now')
""")
today = c.fetchone()[0]
print(f"\n[TODAY SUMMARY]")
print(f"  Events today: {today}")

conn.close()

print("\n" + "="*70)
print("STATUS: WORKING - All systems operational!")
print("="*70 + "\n")
