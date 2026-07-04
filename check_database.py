#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from database import DatabaseManager

print("\n=== DATABASE STATS ===\n")

db = DatabaseManager()
stats = db.get_stats()

print(f"Total events: {stats.get('total_events', 0)}")
print(f"Today: {stats.get('events_today', 0)}")
print(f"Motion: {stats.get('motion_count', 0)}")
print(f"Person: {stats.get('person_detection_count', 0)}")
print(f"Alarm: {stats.get('alarm_count', 0)}")

print("\n=== LAST 5 EVENTS ===\n")

try:
    import sqlite3
    conn = sqlite3.connect('database/events.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM events ORDER BY id DESC LIMIT 5')
    for row in c:
        ts = row["timestamp"][:19] if row["timestamp"] else "N/A"
        print(f"ID {row['id']}: {row['type']:20s} ch{row['channel']} @ {ts}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")

print()
