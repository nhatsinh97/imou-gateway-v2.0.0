#!/usr/bin/env python3
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from mqtt_client import mqtt_manager
from parser import parse_webhook
import time
import json

# Test data - Vietnamese characters
test_event = {
    'channel': 1,
    'cname': 'Chuồng gà',
    'labelType': 'motionAlarm',
    'type': 1,
    'time': 1783202074,
    'did': '5418CADPSFC113A',
    'dname': 'Nhà của sinh'
}

print("[TEST] Parsing webhook with Vietnamese characters...")
event = parse_webhook(test_event)

if event:
    print(f"OK - Event parsed: type={event['type']}, channel={event['channel']}")
    
    print("\n[TEST] Publishing to MQTT...")
    mqtt_manager.connect()
    time.sleep(1)
    
    result = mqtt_manager.publish_event(event)
    print(f"OK - Publish result: {result}")
    
    print("\n[TEST] Event JSON:")
    json_str = json.dumps(event, ensure_ascii=False, indent=2)
    print(json_str)
else:
    print("FAIL - Could not parse event")

