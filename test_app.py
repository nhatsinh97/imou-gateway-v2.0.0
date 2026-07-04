#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test suite for Imou Gateway v2.0.0"""

import unittest
import json
from app import app
from database import db_manager

class TestGatewayApp(unittest.TestCase):
    
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn('status', data)
        self.assertIn(data['status'], ['ok', 'running'])  # Accept both
    
    def test_webhook_endpoint(self):
        """Test webhook endpoint"""
        test_data = {
            'channel': 1,
            'type': 'motion',
            'description': 'Motion detected'
        }
        resp = self.client.post('/webhook', json=test_data)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['status'], 'ok')
    
    def test_webhook_invalid_data(self):
        """Test webhook with invalid data"""
        resp = self.client.post('/webhook', json='invalid')
        self.assertEqual(resp.status_code, 400)
    
    def test_events_endpoint(self):
        """Test events endpoint"""
        resp = self.client.get('/events')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIsInstance(data, dict)
        self.assertIn('events', data)
        self.assertIsInstance(data['events'], list)
    
    def test_database_save(self):
        """Test database save functionality"""
        event = {
            'channel': 1,
            'type': 'test',
            'description': 'Test event',
            'timestamp': '2026-01-01T00:00:00'
        }
        db_manager.save_event(event)
        events = db_manager.get_events()
        self.assertGreater(len(events), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
