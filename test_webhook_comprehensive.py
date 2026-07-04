#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to validate Imou webhook data reception and processing
Simulates real Imou camera webhook events
"""

import json
import requests
import time
from datetime import datetime

# Configuration
GATEWAY_URL = "http://localhost:5000"
WEBHOOK_ENDPOINT = f"{GATEWAY_URL}/webhook"
EVENTS_ENDPOINT = f"{GATEWAY_URL}/events"
HEALTH_ENDPOINT = f"{GATEWAY_URL}/health"

# Color codes for terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(msg):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{msg}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}ℹ {msg}{RESET}")

# Test 1: Check gateway health
def test_gateway_health():
    print_header("TEST 1: Gateway Health Check")
    try:
        resp = requests.get(HEALTH_ENDPOINT, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print_success("Gateway is responding")
            print(f"  Status: {data.get('status')}")
            print(f"  MQTT Connected: {data.get('mqtt_connected')}")
            return True
        else:
            print_error(f"Gateway returned status {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to gateway. Is it running?")
        print_info("Start with: docker-compose up -d")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# Test 2: Send motion detection event (Common Imou format)
def test_motion_event():
    print_header("TEST 2: Motion Detection Event")
    
    # Standard Imou motion event
    event_data = {
        "channel": 1,
        "type": "motion",
        "description": "Motion detected on channel 1",
        "timestamp": datetime.now().isoformat(),
        "device_id": "IMOU-TEST-001",
        "device_name": "Hallway Camera"
    }
    
    print_info(f"Sending event: {json.dumps(event_data, indent=2)}")
    
    try:
        resp = requests.post(WEBHOOK_ENDPOINT, json=event_data, timeout=5)
        
        if resp.status_code == 200:
            result = resp.json()
            print_success(f"Event received and processed")
            print(f"  Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print_error(f"Failed with status {resp.status_code}")
            print(f"  Response: {resp.text}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# Test 3: Send person detection event
def test_person_detection():
    print_header("TEST 3: Person Detection Event")
    
    event_data = {
        "channel": 1,
        "type": "person_detection",
        "description": "Person detected on channel 1",
        "timestamp": datetime.now().isoformat(),
        "device_id": "IMOU-TEST-001",
        "confidence": 0.95
    }
    
    print_info(f"Sending event: {json.dumps(event_data, indent=2)}")
    
    try:
        resp = requests.post(WEBHOOK_ENDPOINT, json=event_data, timeout=5)
        
        if resp.status_code == 200:
            result = resp.json()
            print_success("Event received and processed")
            print(f"  Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print_error(f"Failed with status {resp.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# Test 4: Send alarm event
def test_alarm_event():
    print_header("TEST 4: Alarm Event")
    
    event_data = {
        "channel": 1,
        "type": "alarm",
        "description": "Alarm triggered on channel 1",
        "alarm_type": "motion",
        "timestamp": datetime.now().isoformat(),
        "device_id": "IMOU-TEST-001"
    }
    
    print_info(f"Sending event: {json.dumps(event_data, indent=2)}")
    
    try:
        resp = requests.post(WEBHOOK_ENDPOINT, json=event_data, timeout=5)
        
        if resp.status_code == 200:
            result = resp.json()
            print_success("Event received and processed")
            return True
        else:
            print_error(f"Failed with status {resp.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# Test 5: Send multiple events
def test_multiple_events():
    print_header("TEST 5: Multiple Events (Stress Test)")
    
    events = [
        {"channel": 1, "type": "motion", "description": "Motion on channel 1"},
        {"channel": 2, "type": "motion", "description": "Motion on channel 2"},
        {"channel": 1, "type": "person_detection", "description": "Person on channel 1"},
        {"channel": 2, "type": "alarm", "description": "Alarm on channel 2"},
    ]
    
    success_count = 0
    for i, event in enumerate(events, 1):
        event["timestamp"] = datetime.now().isoformat()
        print_info(f"Event {i}/{len(events)}: {event.get('type')} on channel {event.get('channel')}")
        
        try:
            resp = requests.post(WEBHOOK_ENDPOINT, json=event, timeout=5)
            if resp.status_code == 200:
                success_count += 1
                print_success(f"  Event {i} processed")
            else:
                print_error(f"  Event {i} failed")
        except Exception as e:
            print_error(f"  Event {i} error: {e}")
        
        time.sleep(0.1)  # Small delay between events
    
    print(f"\nProcessed: {success_count}/{len(events)} events successfully")
    return success_count == len(events)

# Test 6: Verify events in database
def test_database_storage():
    print_header("TEST 6: Verify Database Storage")
    
    try:
        resp = requests.get(EVENTS_ENDPOINT, timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            events = data.get('events', [])
            count = len(events)
            
            print_success(f"Retrieved {count} events from database")
            
            if count > 0:
                print_info("Recent events:")
                for event in events[:5]:
                    print(f"  - [{event.get('id')}] {event.get('event_type')} - {event.get('description')}")
                    print(f"    Timestamp: {event.get('timestamp')}")
                    print(f"    Channel: {event.get('channel')}")
                return True
            else:
                print_error("No events in database")
                return False
        else:
            print_error(f"Failed to retrieve events: {resp.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# Test 7: Check statistics
def test_statistics():
    print_header("TEST 7: Database Statistics")
    
    try:
        resp = requests.get(f"{GATEWAY_URL}/stats", timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            stats = data.get('database', {})
            
            print_success("Database statistics retrieved")
            print(f"  Total events: {stats.get('total_events', 0)}")
            
            by_channel = stats.get('by_channel', {})
            if by_channel:
                print("  Events by channel:")
                for channel, count in sorted(by_channel.items()):
                    print(f"    Channel {channel}: {count} events")
            
            by_type = stats.get('by_type', {})
            if by_type:
                print("  Events by type:")
                for event_type, count in sorted(by_type.items()):
                    print(f"    {event_type}: {count} events")
            
            return True
        else:
            print_error(f"Failed to get statistics: {resp.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# Test 8: Test invalid data handling
def test_invalid_data():
    print_header("TEST 8: Invalid Data Handling")
    
    invalid_tests = [
        ("String instead of JSON", "invalid_string"),
        ("Empty object", {}),
        ("Missing required fields", {"random_field": "value"}),
    ]
    
    passed = 0
    for test_name, data in invalid_tests:
        print_info(f"Testing: {test_name}")
        
        try:
            resp = requests.post(WEBHOOK_ENDPOINT, json=data, timeout=5)
            
            # We expect either 400 (bad request) or 200 (graceful handling)
            if resp.status_code in [200, 400]:
                print_success(f"  Handled correctly (status {resp.status_code})")
                passed += 1
            else:
                print_error(f"  Unexpected status: {resp.status_code}")
        except Exception as e:
            print_error(f"  Error: {e}")
    
    return passed == len(invalid_tests)

# Test 9: Filter events by channel
def test_event_filtering():
    print_header("TEST 9: Event Filtering")
    
    try:
        # Get events from channel 1
        resp = requests.get(f"{EVENTS_ENDPOINT}?channel=1", timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            events = data.get('events', [])
            
            print_success(f"Retrieved {len(events)} events from channel 1")
            
            # Verify all events are from channel 1
            all_channel_1 = all(e.get('channel') == 1 for e in events)
            if all_channel_1:
                print_success("All events are from channel 1")
                return True
            else:
                print_error("Some events are not from channel 1")
                return False
        else:
            print_error(f"Failed to retrieve events: {resp.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

# Main test runner
def run_all_tests():
    print_header("IMOU GATEWAY WEBHOOK TEST SUITE")
    
    tests = [
        ("Gateway Health", test_gateway_health),
        ("Motion Detection", test_motion_event),
        ("Person Detection", test_person_detection),
        ("Alarm Event", test_alarm_event),
        ("Multiple Events", test_multiple_events),
        ("Database Storage", test_database_storage),
        ("Statistics", test_statistics),
        ("Invalid Data", test_invalid_data),
        ("Event Filtering", test_event_filtering),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
        
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {status} - {test_name}")
    
    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}✓ All tests passed! Webhook is working correctly!{RESET}\n")
    else:
        print(f"{RED}✗ Some tests failed. Check the output above.{RESET}\n")

if __name__ == "__main__":
    print(f"{BLUE}Imou Gateway v2.0.0 - Webhook Test Suite{RESET}")
    print(f"{BLUE}Testing webhook data reception and processing{RESET}\n")
    
    run_all_tests()
