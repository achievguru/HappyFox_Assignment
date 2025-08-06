"""
Database operations for the Gmail Rule Processor.

This module provides a clean interface for database operations with proper
connection management and error handling.
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from config import DATABASE_NAME

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    
    Ensures proper connection handling and cleanup.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseError(f"Failed to connect to database: {e}")
    finally:
        if conn:
            conn.close()


def init_database() -> None:
    """
    Initialize the database with required tables and indexes.
    
    Creates the emails table, email_labels table, and necessary indexes
    for optimal query performance.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create main emails table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emails (
                    id TEXT PRIMARY KEY,
                    sender TEXT,
                    subject TEXT,
                    body TEXT,
                    received_at TEXT,
                    label_ids TEXT,
                    is_read BOOLEAN
                )
            ''')

            # Create email-labels many-to-many mapping
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_labels (
                    email_id TEXT,
                    label TEXT,
                    PRIMARY KEY (email_id, label),
                    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
                )
            ''')

            # Add indexes for fast querying
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sender ON emails(sender)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_received_at ON emails(received_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_read ON emails(is_read)')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise DatabaseError(f"Database initialization failed: {e}")


def save_email(email_data: Dict[str, Any]) -> None:
    """
    Save email data to the database.
    
    Args:
        email_data: Dictionary containing email information
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Save core email info
            cursor.execute('''
                INSERT OR REPLACE INTO emails (id, sender, subject, body, received_at, label_ids, is_read)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                email_data.get('id'),
                email_data.get('sender'),
                email_data.get('subject'),
                email_data.get('body'),
                email_data.get('received_at'),
                email_data.get('label_ids', ''),
                email_data.get('is_read', False)
            ))

            # Save label mappings
            labels = email_data.get('label_ids', '')
            if labels:
                label_list = [label.strip() for label in labels.split(',') if label.strip()]
                for label in label_list:
                    cursor.execute('''
                        INSERT OR IGNORE INTO email_labels (email_id, label)
                        VALUES (?, ?)
                    ''', (email_data['id'], label))

            conn.commit()
            logger.debug(f"Saved email {email_data.get('id')}")
            
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Failed to save email {email_data.get('id')}: {e}")
        raise DatabaseError(f"Failed to save email: {e}")


def get_all_emails() -> List[Dict[str, Any]]:
    """
    Retrieve all emails from the database.
    
    Returns:
        List of email dictionaries
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, sender, subject, body, received_at, label_ids, is_read 
                FROM emails
            """)
            
            emails = []
            for row in cursor.fetchall():
                emails.append({
                    "id": row['id'],
                    "sender": row['sender'],
                    "subject": row['subject'],
                    "body": row['body'],
                    "received_at": row['received_at'],
                    "label_ids": row['label_ids'],
                    "is_read": bool(row['is_read'])
                })
            
            logger.debug(f"Retrieved {len(emails)} emails from database")
            return emails
            
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve emails: {e}")
        raise DatabaseError(f"Failed to retrieve emails: {e}")


def get_emails_by_condition(condition: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Retrieve emails that match a specific condition.
    
    Args:
        condition: Dictionary containing field, predicate, and value
        
    Returns:
        List of matching email dictionaries
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            field = condition.get('field')
            predicate = condition.get('predicate')
            value = condition.get('value')
            
            # Build query based on condition
            if field == 'received_at' and predicate in ['less_than_days', 'greater_than_days']:
                # Handle date-based queries
                if predicate == 'less_than_days':
                    cursor.execute("""
                        SELECT id, sender, subject, body, received_at, label_ids, is_read 
                        FROM emails 
                        WHERE received_at > datetime('now', '-{} days')
                    """.format(value))
                else:  # greater_than_days
                    cursor.execute("""
                        SELECT id, sender, subject, body, received_at, label_ids, is_read 
                        FROM emails 
                        WHERE received_at < datetime('now', '-{} days')
                    """.format(value))
            else:
                # Handle text-based queries
                cursor.execute("""
                    SELECT id, sender, subject, body, received_at, label_ids, is_read 
                    FROM emails 
                    WHERE {} LIKE ?
                """.format(field), (f'%{value}%',))
            
            emails = []
            for row in cursor.fetchall():
                emails.append({
                    "id": row['id'],
                    "sender": row['sender'],
                    "subject": row['subject'],
                    "body": row['body'],
                    "received_at": row['received_at'],
                    "label_ids": row['label_ids'],
                    "is_read": bool(row['is_read'])
                })
            
            logger.debug(f"Retrieved {len(emails)} emails matching condition")
            return emails
            
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve emails by condition: {e}")
        raise DatabaseError(f"Failed to retrieve emails by condition: {e}") 
