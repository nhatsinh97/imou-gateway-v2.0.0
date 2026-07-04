#!/usr/bin/env python3
"""
Test parser with real PaaS format webhook data from logs
"""
import sys
sys.path.insert(0, '.')

import io
# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from parser import parse_webhook
import json

# Real PaaS format events from the log
paas_events = [
    {
        "name": "IPC Human Detection (type 120)",
        "data": {
            'accessType': 'PaaS',
            'action': 'start',
            'cid': 0,
            'cname': 'Cong',  # Simplified to ASCII
            'deviceType': 'IPC',
            'did': '9M0776CPCGF08E9',
            'dname': 'Cong',
            'id': 2049510200225024,
            'labelType': 'humanAlarm',
            'msgType': 'human',
            'time': 1783201662,
            'utcTime': 1783176462,
        }
    },
    {
        "name": "NVR Human Detection (type 10039)",
        "data": {
            'accessType': 'PaaS',
            'action': 'start',
            'cid': 3,
            'cname': 'Overview',
            'deviceType': 'NVR',
            'did': '5418CADPSFC113A',
            'dname': 'Home',
            'id': 800464991668480,
            'labelType': 'humanAlarm',
            'msgType': 'smdHuman',
            'type': 10039,
            'time': 1783201663,
            'utcTime': 1783176463,
        }
    },
    {
        "name": "Motion Detection (type 1 - local format)",
        "data": {
            'channel': 1,
            'type': '1',
            'description': 'Motion detected',
            'timestamp': '2026-07-04 14:31:18'
        }
    }
]

print("\n" + "="*70)
print("Testing Parser with PaaS Format Events")
print("="*70)

test_count = 0
pass_count = 0

for test_case in paas_events:
    test_count += 1
    print(f"\n[TEST {test_count}] {test_case['name']}")
    print(f"  Input type: {test_case['data'].get('type', 'N/A')}")
    
    event = parse_webhook(test_case['data'])
    
    if event:
        pass_count += 1
        print(f"  PASS - Parsed successfully")
        print(f"    Type: {event['type']}")
        print(f"    Channel: {event['channel']}")
        print(f"    Description: {event['description']}")
        print(f"    Device: {event['device_name']} ({event['device_id']})")
        print(f"    Timestamp: {event['timestamp']}")
    else:
        print(f"  FAIL - Could not parse")

print("\n" + "="*70)
print(f"Results: {pass_count}/{test_count} tests passed")
print("="*70 + "\n")
