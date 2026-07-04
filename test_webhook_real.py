#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to validate Imou webhook data reception and processing
Simulates real Imou camera webhook events (Fixed Unicode)
"""

import json
import time
from datetime import datetime
from flask import Flask, json as flask_json
from app import app
from database import db_manager

# Test configuration
test_results = []

def test_header(msg):
    print("\n" + "="*60)
    print(msg)
    print("="*60 + "\n")

def test_pass(msg):
    print("[PASS] " + msg)
    test_results.append(("PASS", msg))

def test_fail(msg):
    print("[FAIL] " + msg)
    test_results.append(("FAIL", msg))

def test_info(msg):
    print("[INFO] " + msg)

# Test 1: Test webhook endpoint with motion event
def test_webhook_motion():
    test_header("TEST 1: Motion Detection Webhook")
    
    with app.test_client() as client:
        event_data = {
            "channel": 1,
            "type": "motion",
            "description": "Motion detected on channel 1",
            "timestamp": datetime.now().isoformat(),
            "device_id": "IMOU-TEST-001"
        }
        
        test_info("Sending motion event...")
        test_info(f"Event: {json.dumps(event_data, ensure_ascii=False, indent=2)}")
        
        resp = client.post('/webhook', json=event_data)
        
        if resp.status_code == 200:
            data = json.loads(resp.data)
            if data.get('status') == 'ok':
                test_pass("Motion event received and processed")
                return True
            else:
                test_fail(f"Unexpected response: {data}")
                return False
        else:
            test_fail(f"Failed with status {resp.status_code}: {resp.data.decode()}")
            return False

# Test 2: Test webhook with person detection
def test_webhook_person():
    test_header("TEST 2: Person Detection Webhook")
    
    with app.test_client() as client:
        event_data = {
            "channel": 1,
            "type": "person_detection",
            "description": "Person detected",
            "timestamp": datetime.now().isoformat(),
            "device_id": "IMOU-TEST-001",
            "confidence": 0.95
        }
        
        test_info("Sending person detection event...")
        resp = client.post('/webhook', json=event_data)
        
        if resp.status_code == 200:
            test_pass("Person detection event received")
            return True
        else:
            test_fail(f"Failed with status {resp.status_code}")
            return False

# Test 3: Test webhook with alarm
def test_webhook_alarm():
    test_header("TEST 3: Alarm Event Webhook")
    
    with app.test_client() as client:
        event_data = {
            "channel": 2,
            "type": "alarm",
            "description": "Alarm triggered",
            "alarm_type": "motion",
            "timestamp": datetime.now().isoformat()
        }
        
        test_info("Sending alarm event...")
        resp = client.post('/webhook', json=event_data)
        
        if resp.status_code == 200:
            test_pass("Alarm event received")
            return True
        else:
            test_fail(f"Failed with status {resp.status_code}")
            return False

# Test 4: Test multiple events
def test_multiple_webhooks():
    test_header("TEST 4: Multiple Events (Stress Test)")
    
    with app.test_client() as client:
        events = [
            {"channel": 1, "type": "motion", "description": "Motion ch1"},
            {"channel": 2, "type": "motion", "description": "Motion ch2"},
            {"channel": 1, "type": "person_detection", "description": "Person ch1"},
            {"channel": 2, "type": "alarm", "description": "Alarm ch2"},
        ]
        
        success = 0
        for i, event in enumerate(events, 1):
            event["timestamp"] = datetime.now().isoformat()
            test_info(f"Event {i}/{len(events)}: {event['type']}")
            
            resp = client.post('/webhook', json=event)
            if resp.status_code == 200:
                success += 1
            
            time.sleep(0.1)
        
        if success == len(events):
            test_pass(f"All {len(events)} events processed successfully")
            return True
        else:
            test_fail(f"Only {success}/{len(events)} events processed")
            return False

# Test 5: Verify database storage
def test_database_events():
    test_header("TEST 5: Database Event Storage")
    
    test_info("Querying database for events...")
    events = db_manager.get_events(limit=100)
    
    if events:
        test_pass(f"Found {len(events)} events in database")
        test_info("Recent events:")
        for event in events[:5]:
            print(f"  - ID: {event.get('id')}, Type: {event.get('event_type')}, Channel: {event.get('channel')}")
            print(f"    Timestamp: {event.get('timestamp')}")
        return True
    else:
        test_fail("No events in database")
        return False

# Test 6: Test statistics
def test_database_stats():
    test_header("TEST 6: Database Statistics")
    
    try:
        stats = db_manager.get_stats()
        
        test_info(f"Total events: {stats.get('total_events', 0)}")
        
        by_channel = stats.get('by_channel', {})
        if by_channel:
            test_info("Events by channel:")
            for channel, count in sorted(by_channel.items()):
                print(f"  Channel {channel}: {count}")
        
        by_type = stats.get('by_type', {})
        if by_type:
            test_info("Events by type:")
            for event_type, count in sorted(by_type.items()):
                print(f"  {event_type}: {count}")
        
        if stats.get('total_events', 0) > 0:
            test_pass("Database statistics retrieved")
            return True
        else:
            test_fail("No statistics available")
            return False
    
    except Exception as e:
        test_fail(f"Error: {str(e)}")
        return False

# Test 7: Test event filtering
def test_filter_by_channel():
    test_header("TEST 7: Event Filtering by Channel")
    
    with app.test_client() as client:
        # Get events from channel 1
        resp = client.get('/events?channel=1')
        
        if resp.status_code == 200:
            data = json.loads(resp.data)
            events = data.get('events', [])
            
            # Check all events are from channel 1
            all_ch1 = all(e.get('channel') == 1 for e in events if e.get('channel') is not None)
            
            if all_ch1:
                test_pass(f"Filtered {len(events)} events from channel 1")
                return True
            else:
                test_fail("Some filtered events are not from channel 1")
                return False
        else:
            test_fail(f"Failed with status {resp.status_code}")
            return False

# Test 8: Test invalid data handling
def test_invalid_data():
    test_header("TEST 8: Invalid Data Handling")
    
    with app.test_client() as client:
        # Send invalid data (string instead of dict)
        resp = client.post('/webhook', json="invalid_string")
        
        if resp.status_code == 400:
            test_pass("Invalid data correctly rejected with 400")
            return True
        elif resp.status_code == 200:
            test_pass("Invalid data handled gracefully")
            return True
        else:
            test_fail(f"Unexpected response code: {resp.status_code}")
            return False

# Test 9: Test health endpoint
def test_health_endpoint():
    test_header("TEST 9: Health Endpoint")
    
    with app.test_client() as client:
        resp = client.get('/health')
        
        if resp.status_code == 200:
            data = json.loads(resp.data)
            test_pass("Health endpoint is working")
            test_info(f"Status: {data.get('status')}")
            test_info(f"MQTT Connected: {data.get('mqtt_connected')}")
            return True
        else:
            test_fail(f"Health check failed: {resp.status_code}")
            return False

# Test 10: Test events endpoint
def test_events_endpoint():
    test_header("TEST 10: Events Endpoint")
    
    with app.test_client() as client:
        resp = client.get('/events')
        
        if resp.status_code == 200:
            data = json.loads(resp.data)
            count = len(data.get('events', []))
            test_pass(f"Events endpoint returned {count} events")
            return True
        else:
            test_fail(f"Events endpoint failed: {resp.status_code}")
            return False

# Test 11: Test parser with various formats
def test_parser_formats():
    test_header("TEST 11: Parser - Various Imou Formats")
    
    from parser import parse_webhook
    
    test_cases = [
        {
            "name": "Standard format",
            "data": {"channel": 1, "type": "motion", "description": "Motion"}
        },
        {
            "name": "Alternative field names",
            "data": {"chn": 1, "event_type": "motion", "msg": "Motion"}
        },
        {
            "name": "With device info",
            "data": {"channel": 1, "type": "motion", "device_id": "ABC123", "device_name": "Front Door"}
        },
        {
            "name": "Person detection",
            "data": {"channel": 1, "type": "person_detection", "confidence": 0.95}
        },
        {
            "name": "Various event types",
            "data": {"channel": 1, "type": "vehicle_detection", "description": "Vehicle"}
        }
    ]
    
    passed = 0
    for test_case in test_cases:
        result = parse_webhook(test_case["data"])
        if result:
            test_info(f"OK - {test_case['name']}: {result['type']}")
            passed += 1
        else:
            test_info(f"FAIL - {test_case['name']}")
    
    if passed == len(test_cases):
        test_pass(f"All {len(test_cases)} parser tests passed")
        return True
    else:
        test_fail(f"Only {passed}/{len(test_cases)} parser tests passed")
        return False

# Main test runner
def run_all_tests():
    test_header("IMOU GATEWAY WEBHOOK TEST SUITE")
    
    tests = [
        test_webhook_motion,
        test_webhook_person,
        test_webhook_alarm,
        test_multiple_webhooks,
        test_database_events,
        test_database_stats,
        test_filter_by_channel,
        test_invalid_data,
        test_health_endpoint,
        test_events_endpoint,
        test_parser_formats,
    ]
    
    for test_func in tests:
        try:
            test_func()
        except Exception as e:
            test_fail(f"{test_func.__name__} crashed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Summary
    test_header("TEST SUMMARY")
    
    passed = sum(1 for status, _ in test_results if status == "PASS")
    failed = sum(1 for status, _ in test_results if status == "FAIL")
    total = len(test_results)
    
    for status, msg in test_results:
        prefix = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"{prefix} {msg}")
    
    print("\n" + "="*60)
    print(f"TOTAL: {passed} PASS, {failed} FAIL, {total} tests")
    print("="*60 + "\n")
    
    if failed == 0:
        print("SUCCESS: All tests passed! Webhook is working correctly!")
    else:
        print(f"WARNING: {failed} test(s) failed. Check output above.")
    
    return failed == 0

if __name__ == "__main__":
    print("\nImou Gateway v2.0.0 - Webhook Test Suite")
    print("Testing webhook data reception and processing\n")
    
    success = run_all_tests()
    exit(0 if success else 1)
