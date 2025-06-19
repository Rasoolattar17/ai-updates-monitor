import sqlite3
import logging
from datetime import datetime
from config import DATABASE_PATH

class AIMonitoringDB:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
        
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create table for tracking monitored items
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS monitored_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_type TEXT NOT NULL,
                        source_name TEXT NOT NULL,
                        item_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        url TEXT,
                        content TEXT,
                        published_date DATETIME,
                        discovered_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        notified BOOLEAN DEFAULT FALSE,
                        UNIQUE(source_type, source_name, item_id)
                    )
                ''')
                
                # Create table for notification history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notification_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_id INTEGER,
                        notification_type TEXT NOT NULL,
                        sent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT,
                        FOREIGN KEY (item_id) REFERENCES monitored_items (id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_source_item 
                    ON monitored_items(source_type, source_name, item_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_notified 
                    ON monitored_items(notified)
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except Exception as e:
            logging.error(f"Database initialization error: {e}")
            raise
    
    def is_item_exists(self, source_type, source_name, item_id):
        """Check if an item already exists in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM monitored_items 
                    WHERE source_type = ? AND source_name = ? AND item_id = ?
                ''', (source_type, source_name, item_id))
                
                return cursor.fetchone()[0] > 0
                
        except Exception as e:
            logging.error(f"Error checking item existence: {e}")
            return False
    
    def add_item(self, source_type, source_name, item_id, title, url=None, content=None, published_date=None):
        """Add a new monitored item to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO monitored_items 
                    (source_type, source_name, item_id, title, url, content, published_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (source_type, source_name, item_id, title, url, content, published_date))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logging.error(f"Error adding item to database: {e}")
            return None
    
    def get_unnotified_items(self):
        """Get all items that haven't been notified yet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, source_type, source_name, title, url, content, published_date, discovered_date
                    FROM monitored_items 
                    WHERE notified = FALSE
                    ORDER BY discovered_date DESC, published_date DESC
                ''')
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logging.error(f"Error getting unnotified items: {e}")
            return []
    
    def mark_as_notified(self, item_id, notification_type="email", success=True, error_message=None):
        """Mark an item as notified"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update the monitored item
                cursor.execute('''
                    UPDATE monitored_items 
                    SET notified = TRUE 
                    WHERE id = ?
                ''', (item_id,))
                
                # Add to notification history
                cursor.execute('''
                    INSERT INTO notification_history 
                    (item_id, notification_type, success, error_message)
                    VALUES (?, ?, ?, ?)
                ''', (item_id, notification_type, success, error_message))
                
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"Error marking item as notified: {e}")
            return False
    
    def get_recent_items(self, days=7):
        """Get items discovered in the last N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT source_type, source_name, title, url, discovered_date
                    FROM monitored_items 
                    WHERE discovered_date >= datetime('now', '-{} days')
                    ORDER BY discovered_date DESC
                '''.format(days))
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logging.error(f"Error getting recent items: {e}")
            return []
    
    def cleanup_old_items(self, days=30):
        """Remove items older than N days to keep database size manageable"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM monitored_items 
                    WHERE discovered_date < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                logging.info(f"Cleaned up {deleted_count} old items from database")
                return deleted_count
                
        except Exception as e:
            logging.error(f"Error cleaning up old items: {e}")
            return 0 