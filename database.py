# SQLite helper with connection pooling and optimization
import sqlite3
import json
import os
from datetime import datetime
from config import config
from pathlib import Path

class DatabaseManager:
    
    def __init__(self):
        self.db_path = config.get("database.path", "database/events.db")
        
        # Ensure database directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            Path(db_dir).mkdir(parents=True, exist_ok=True)
        
        self._init_db()
    
    def _get_connection(self):
        """Get database connection with optimizations"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode = WAL")
        
        # Performance optimizations
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = -64000")
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA query_only = FALSE")
        
        # Set row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        return conn
    
    def _init_db(self):
        """Initialize database with optimized schema"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                channel INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT,
                raw_data TEXT
            )
        ''')
        
        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON events (timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_channel 
            ON events (channel)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_event_type 
            ON events (event_type)
        ''')
        
        # Create metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add cleanup policy info
        cursor.execute('''
            INSERT OR IGNORE INTO metadata (key, value)
            VALUES ('db_version', '1')
        ''')
        
        conn.commit()
        conn.close()
    
    def save_event(self, event):
        """Save event to database efficiently"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO events (channel, event_type, description, raw_data)
                VALUES (?, ?, ?, ?)
            ''', (
                event.get('channel', 0),
                event.get('type', 'unknown'),
                event.get('description', ''),
                json.dumps(event, ensure_ascii=False)
            ))
            
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_events(self, limit=50, channel=None, event_type=None):
        """Get recent events with optional filtering"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = 'SELECT id, timestamp, channel, event_type, description FROM events'
            params = []
            
            # Add filters
            where_clauses = []
            if channel is not None:
                where_clauses.append('channel = ?')
                params.append(channel)
            if event_type:
                where_clauses.append('event_type = ?')
                params.append(event_type)
            
            if where_clauses:
                query += ' WHERE ' + ' AND '.join(where_clauses)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return results
        finally:
            conn.close()
    
    def cleanup_old_events(self, days=30):
        """Remove events older than specified days"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM events 
                WHERE timestamp < datetime('now', ? || ' days')
            ''', (f'-{days}',))
            
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def get_stats(self):
        """Get database statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Total events
            cursor.execute('SELECT COUNT(*) as count FROM events')
            total = cursor.fetchone()['count']
            
            # Events by channel
            cursor.execute('''
                SELECT channel, COUNT(*) as count 
                FROM events 
                GROUP BY channel
                ORDER BY channel
            ''')
            channels = {row['channel']: row['count'] for row in cursor.fetchall()}
            
            # Events by type
            cursor.execute('''
                SELECT event_type, COUNT(*) as count 
                FROM events 
                GROUP BY event_type
                ORDER BY event_type
            ''')
            types = {row['event_type']: row['count'] for row in cursor.fetchall()}
            
            return {
                'total_events': total,
                'by_channel': channels,
                'by_type': types
            }
        finally:
            conn.close()

db_manager = DatabaseManager()

