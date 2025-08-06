"""
Gmail API authentication module.

This module handles authentication with the Gmail API using OAuth 2.0.
"""

import os
import logging
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import GMAIL_SCOPES, CREDENTIALS_FILE, TOKEN_FILE

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Custom exception for authentication-related errors."""
    pass


def get_gmail_service():
    """
    Authenticate and return a Gmail API service object.
    
    Returns:
        Gmail API service object
        
    Raises:
        AuthenticationError: If authentication fails
    """
    try:
        creds = _load_existing_credentials()
        
        if not creds or not creds.valid:
            creds = _refresh_or_create_credentials(creds)
            _save_credentials(creds)
        
        service = build('gmail', 'v1', credentials=creds)
        logger.info("Successfully authenticated with Gmail API")
        return service
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise AuthenticationError(f"Failed to authenticate with Gmail API: {e}")


def _load_existing_credentials() -> Optional[Credentials]:
    """
    Load existing credentials from token file.
    
    Returns:
        Credentials object if valid token exists, None otherwise
    """
    try:
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, GMAIL_SCOPES)
            logger.debug("Loaded existing credentials from token file")
            return creds
        else:
            logger.debug("No existing token file found")
            return None
            
    except Exception as e:
        logger.warning(f"Failed to load existing credentials: {e}")
        return None


def _refresh_or_create_credentials(creds: Optional[Credentials]) -> Credentials:
    """
    Refresh existing credentials or create new ones.
    
    Args:
        creds: Existing credentials object or None
        
    Returns:
        Valid credentials object
        
    Raises:
        AuthenticationError: If credentials cannot be refreshed or created
    """
    try:
        # Try to refresh existing credentials
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials")
            creds.refresh(Request())
            return creds
        
        # Create new credentials
        if not os.path.exists(CREDENTIALS_FILE):
            raise AuthenticationError(f"Credentials file not found: {CREDENTIALS_FILE}")
        
        logger.info("Creating new credentials via OAuth flow")
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, GMAIL_SCOPES)
        creds = flow.run_local_server(port=0)
        return creds
        
    except Exception as e:
        logger.error(f"Failed to refresh or create credentials: {e}")
        raise AuthenticationError(f"Credential refresh/creation failed: {e}")


def _save_credentials(creds: Credentials) -> None:
    """
    Save credentials to token file.
    
    Args:
        creds: Credentials object to save
    """
    try:
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        logger.debug("Saved credentials to token file")
        
    except Exception as e:
        logger.error(f"Failed to save credentials: {e}")
        raise AuthenticationError(f"Failed to save credentials: {e}")


def revoke_credentials() -> None:
    """
    Revoke stored credentials and remove token file.
    
    This is useful for testing or when credentials need to be reset.
    """
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            logger.info("Removed token file")
        else:
            logger.debug("No token file to remove")
            
    except Exception as e:
        logger.error(f"Failed to revoke credentials: {e}")
        raise AuthenticationError(f"Failed to revoke credentials: {e}")


def is_authenticated() -> bool:
    """
    Check if valid credentials exist.
    
    Returns:
        True if valid credentials exist, False otherwise
    """
    try:
        creds = _load_existing_credentials()
        return creds is not None and creds.valid
    except Exception:
        return False
