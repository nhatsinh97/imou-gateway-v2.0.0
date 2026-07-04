#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test parser with actual Imou camera data from /events
"""

from parser import parse_webhook
import json

print("\n" + "="*60)
print("TEST: Parser with Real Imou Camera Data")
print("="*60 + "\n")

# Test data from actual /events endpoint
test_cases = [
    {
        "name": "Real Imou Event (ID 19)",
        "data": {
            "channel": 0,
            "description": "",
            "event_type": "1",
            "timestamp": "2026-07-04 14:31:18"
        },
        "expected_type": "motion"
    },
    {
        "name": "Real Imou Event (ID 18 - Alarm)",
        "data": {
            "channel": 2,
            "description": "Alarm ch2",
            "event_type": "alarm",
            "timestamp": "2026-07-04 14:25:07"
        },
        "expected_type": "alarm"
    },
    {
        "name": "Imou Event Code '3' (Alarm)",
        "data": {
            "channel": 0,
            "event_type": "3",
            "description": "",
            "timestamp": "2026-07-04 14:31:18"
        },
        "expected_type": "alarm"
    },
    {
        "name": "Imou Event Code '2' (Person)",
        "data": {
            "channel": 0,
            "event_type": "2",
            "description": "",
            "timestamp": "2026-07-04 14:31:18"
        },
        "expected_type": "person_detection"
    },
    {
        "name": "Imou Event Code '5' (Vehicle)",
        "data": {
            "channel": 0,
            "event_type": "5",
            "description": "",
            "timestamp": "2026-07-04 14:31:18"
        },
        "expected_type": "vehicle_detection"
    },
    {
        "name": "Standard Format (Test Data)",
        "data": {
            "channel": 1,
            "type": "motion",
            "description": "Motion detected",
            "timestamp": "2026-07-04T14:31:18"
        },
        "expected_type": "motion"
    },
]

passed = 0
failed = 0

for test_case in test_cases:
    print(f"Test: {test_case['name']}")
    print(f"Input: {json.dumps(test_case['data'], indent=2)}")
    
    result = parse_webhook(test_case['data'])
    
    if result:
        print(f"Output:")
        print(f"  Channel: {result.get('channel')}")
        print(f"  Type: {result.get('type')}")
        print(f"  Description: {result.get('description')}")
        print(f"  Timestamp: {result.get('timestamp')}")
        
        if result.get('type') == test_case['expected_type']:
            print("Result: PASS - Event type correctly mapped\n")
            passed += 1
        else:
            print(f"Result: FAIL - Expected '{test_case['expected_type']}', got '{result.get('type')}'\n")
            failed += 1
    else:
        print("Result: FAIL - Parser returned None\n")
        failed += 1

print("="*60)
print(f"SUMMARY: {passed} PASS, {failed} FAIL out of {len(test_cases)} tests")
print("="*60 + "\n")

if failed == 0:
    print("SUCCESS: Parser correctly handles real Imou camera data!\n")
else:
    print(f"WARNING: {failed} test(s) failed\n")
