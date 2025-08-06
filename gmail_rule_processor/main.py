"""
Main entry point for the Gmail Rule Processor.

This module orchestrates the email fetching and rule processing workflow.
"""

import logging
import sys
from typing import Optional
from config import LOG_LEVEL, LOG_FORMAT
from gmail_auth import get_gmail_service, AuthenticationError
from gmail_fetcher import fetch_and_store_emails, EmailFetchError
from rule_engine import apply_rules, RuleEngineError
from database import init_database, DatabaseError


def setup_logging() -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('gmail_processor.log')
        ]
    )


def main() -> None:
    """
    Main application entry point.
    
    Orchestrates the email fetching and rule processing workflow.
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Gmail Rule Processor")
        
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        
        # Authenticate with Gmail
        logger.info("Authenticating with Gmail API...")
        service = get_gmail_service()
        
        # Fetch and store emails
        logger.info("Fetching emails from Gmail...")
        fetch_and_store_emails(service)
        
        # Apply rules
        logger.info("Applying email rules...")
        apply_rules(service)
        
        logger.info("Gmail Rule Processor completed successfully")
        
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        sys.exit(1)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)
    except EmailFetchError as e:
        logger.error(f"Email fetching failed: {e}")
        sys.exit(1)
    except RuleEngineError as e:
        logger.error(f"Rule processing failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main()
