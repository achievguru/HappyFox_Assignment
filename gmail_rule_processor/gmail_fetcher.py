"""
Gmail email fetching module.

This module handles fetching emails from Gmail API and storing them in the database.
"""

import logging
import base64
import email
from datetime import datetime
from typing import Dict, Any, Optional, List
from googleapiclient.discovery import Resource
from config import USER_ID, DEFAULT_MAX_EMAILS
from database import save_email, DatabaseError

logger = logging.getLogger(__name__)


class EmailFetchError(Exception):
    """Custom exception for email fetching errors."""
    pass


def fetch_and_store_emails(service: Resource, max_results: int = DEFAULT_MAX_EMAILS) -> None:
    """
    Fetch emails from Gmail and store them in the database.
    
    Args:
        service: Gmail API service object
        max_results: Maximum number of emails to fetch
        
    Raises:
        EmailFetchError: If email fetching fails
    """
    try:
        logger.info(f"Fetching up to {max_results} emails from Gmail")
        
        # Get list of message IDs
        messages = _get_message_list(service, max_results)
        logger.info(f"Found {len(messages)} messages to process")
        
        # Process each message
        processed_count = 0
        for msg in messages:
            try:
                email_data = _fetch_single_email(service, msg['id'])
                save_email(email_data)
                processed_count += 1
                logger.debug(f"Processed email {email_data['id']}")
                
            except Exception as e:
                logger.error(f"Failed to process message {msg['id']}: {e}")
                continue
        
        logger.info(f"Successfully processed {processed_count} emails")
        
    except Exception as e:
        logger.error(f"Email fetching failed: {e}")
        raise EmailFetchError(f"Failed to fetch emails: {e}")


def _get_message_list(service: Resource, max_results: int) -> List[Dict[str, str]]:
    """
    Get list of message IDs from Gmail.
    
    Args:
        service: Gmail API service object
        max_results: Maximum number of messages to retrieve
        
    Returns:
        List of message dictionaries with 'id' key
        
    Raises:
        EmailFetchError: If message list retrieval fails
    """
    try:
        results = service.users().messages().list(
            userId=USER_ID, 
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        logger.debug(f"Retrieved {len(messages)} message IDs")
        return messages
        
    except Exception as e:
        logger.error(f"Failed to get message list: {e}")
        raise EmailFetchError(f"Failed to get message list: {e}")


def _fetch_single_email(service: Resource, message_id: str) -> Dict[str, Any]:
    """
    Fetch a single email by its ID.
    
    Args:
        service: Gmail API service object
        message_id: Gmail message ID
        
    Returns:
        Dictionary containing email data
        
    Raises:
        EmailFetchError: If email fetching fails
    """
    try:
        msg_data = service.users().messages().get(
            userId=USER_ID, 
            id=message_id, 
            format='full'
        ).execute()
        
        return _parse_email_data(msg_data)
        
    except Exception as e:
        logger.error(f"Failed to fetch email {message_id}: {e}")
        raise EmailFetchError(f"Failed to fetch email {message_id}: {e}")


def _parse_email_data(msg_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse Gmail message data into our email format.
    
    Args:
        msg_data: Raw Gmail message data
        
    Returns:
        Parsed email data dictionary
    """
    payload = msg_data.get('payload', {})
    headers = payload.get('headers', [])
    
    email_data = {
        'id': msg_data.get('id'),
        'label_ids': ','.join(msg_data.get('labelIds', [])),
        'is_read': 'UNREAD' not in msg_data.get('labelIds', []),
        'body': extract_body(payload)
    }
    
    # Extract headers
    for header in headers:
        name = header.get('name', '').lower()
        value = header.get('value', '')
        
        if name == 'from':
            email_data['sender'] = value
        elif name == 'subject':
            email_data['subject'] = value
        elif name == 'date':
            email_data['received_at'] = _parse_date_header(value)
    
    # Set defaults for missing fields
    email_data.setdefault('sender', 'Unknown')
    email_data.setdefault('subject', 'No Subject')
    email_data.setdefault('received_at', datetime.utcnow().isoformat())
    
    return email_data


def _parse_date_header(date_string: str) -> str:
    """
    Parse email date header into ISO format.
    
    Args:
        date_string: Date string from email header
        
    Returns:
        ISO format date string
    """
    try:
        parsed_date = email.utils.parsedate_to_datetime(date_string)
        return parsed_date.isoformat()
    except Exception as e:
        logger.warning(f"Failed to parse date '{date_string}': {e}")
        return datetime.utcnow().isoformat()


def extract_body(payload: Dict[str, Any]) -> str:
    """
    Extract email body from Gmail payload.
    
    Args:
        payload: Gmail message payload
        
    Returns:
        Email body as string
    """
    try:
        # Handle multipart messages
        parts = payload.get('parts')
        if parts:
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        return _decode_body_data(data)
        
        # Handle simple messages
        body = payload.get('body', {}).get('data')
        if body:
            return _decode_body_data(body)
        
        return ''
        
    except Exception as e:
        logger.warning(f"Failed to extract email body: {e}")
        return ''


def _decode_body_data(data: str) -> str:
    """
    Decode base64-encoded email body data.
    
    Args:
        data: Base64-encoded string
        
    Returns:
        Decoded string
    """
    try:
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    except Exception as e:
        logger.warning(f"Failed to decode body data: {e}")
        return ''


def get_email_count(service: Resource) -> int:
    """
    Get total number of emails in the account.
    
    Args:
        service: Gmail API service object
        
    Returns:
        Total number of emails
    """
    try:
        results = service.users().messages().list(userId=USER_ID, maxResults=1).execute()
        return results.get('resultSizeEstimate', 0)
    except Exception as e:
        logger.error(f"Failed to get email count: {e}")
        return 0
