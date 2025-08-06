"""
Configuration settings for the Gmail Rule Processor.

This module centralizes all configuration values to make the application
easier to maintain and configure.
"""

import os
from typing import List

# Database Configuration
DATABASE_NAME = 'emails.db'

# Gmail API Configuration
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

# Email Processing Configuration
DEFAULT_MAX_EMAILS = 20
DEFAULT_RULES_FILE = 'rules.json'

# Gmail Labels
UNREAD_LABEL = 'UNREAD'
USER_ID = 'me'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Supported email fields for rule evaluation
SUPPORTED_FIELDS = ['sender', 'subject', 'body', 'received_at', 'is_read']

# Supported predicates for rule evaluation
SUPPORTED_PREDICATES = [
    'contains', 'not_contains', 'equals', 'not_equals',
    'less_than_days', 'greater_than_days'
]

# Supported actions
SUPPORTED_ACTIONS = ['mark_read', 'mark_unread']
MOVE_ACTION_PREFIX = 'move:' 
