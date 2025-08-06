"""
Gmail actions module for performing operations on emails.

This module handles various actions that can be performed on Gmail messages
such as marking as read/unread and moving to labels.
"""

import logging
from typing import List, Dict, Any
from config import USER_ID, UNREAD_LABEL, SUPPORTED_ACTIONS, MOVE_ACTION_PREFIX

logger = logging.getLogger(__name__)


class ActionError(Exception):
    """Custom exception for action-related errors."""
    pass


def perform_actions(service, email_id: str, actions: List[str]) -> None:
    """
    Perform a list of actions on a Gmail message.
    
    Args:
        service: Gmail API service object
        email_id: ID of the email to perform actions on
        actions: List of action strings to perform
        
    Raises:
        ActionError: If any action fails to execute
    """
    if not actions:
        logger.warning(f"No actions specified for email {email_id}")
        return
    
    logger.info(f"Performing {len(actions)} actions on email {email_id}")
    
    for action in actions:
        try:
            _perform_single_action(service, email_id, action)
            logger.debug(f"Successfully performed action '{action}' on email {email_id}")
        except Exception as e:
            logger.error(f"Failed to perform action '{action}' on email {email_id}: {e}")
            raise ActionError(f"Action '{action}' failed: {e}")


def _perform_single_action(service, email_id: str, action: str) -> None:
    """
    Perform a single action on a Gmail message.
    
    Args:
        service: Gmail API service object
        email_id: ID of the email to perform action on
        action: Action string to perform
        
    Raises:
        ActionError: If action is not supported or fails
    """
    if action in SUPPORTED_ACTIONS:
        _perform_basic_action(service, email_id, action)
    elif action.startswith(MOVE_ACTION_PREFIX):
        _perform_move_action(service, email_id, action)
    else:
        raise ActionError(f"Unsupported action: {action}")


def _perform_basic_action(service, email_id: str, action: str) -> None:
    """
    Perform basic actions like mark_read and mark_unread.
    
    Args:
        service: Gmail API service object
        email_id: ID of the email to perform action on
        action: Basic action to perform
    """
    if action == 'mark_read':
        service.users().messages().modify(
            userId=USER_ID,
            id=email_id,
            body={'removeLabelIds': [UNREAD_LABEL]}
        ).execute()
        logger.debug(f"Marked email {email_id} as read")
        
    elif action == 'mark_unread':
        service.users().messages().modify(
            userId=USER_ID,
            id=email_id,
            body={'addLabelIds': [UNREAD_LABEL]}
        ).execute()
        logger.debug(f"Marked email {email_id} as unread")
        
    else:
        raise ActionError(f"Unknown basic action: {action}")


def _perform_move_action(service, email_id: str, action: str) -> None:
    """
    Perform move action to add a label to an email.
    
    Args:
        service: Gmail API service object
        email_id: ID of the email to move
        action: Move action string (format: "move:label_name")
    """
    try:
        label_name = action.split(':', 1)[1]
        if not label_name:
            raise ActionError("Label name cannot be empty")
            
        label_id = get_or_create_label(service, label_name)
        logger.debug(f"Using label ID {label_id} for label '{label_name}'")
        
        service.users().messages().modify(
            userId=USER_ID,
            id=email_id,
            body={'addLabelIds': [label_id]}
        ).execute()
        
        logger.debug(f"Moved email {email_id} to label '{label_name}'")
        
    except IndexError:
        raise ActionError(f"Invalid move action format: {action}")
    except Exception as e:
        raise ActionError(f"Failed to move email: {e}")


def get_or_create_label(service, label_name: str) -> str:
    """
    Get or create a Gmail label.
    
    Args:
        service: Gmail API service object
        label_name: Name of the label to get or create
        
    Returns:
        Label ID string
        
    Raises:
        ActionError: If label operations fail
    """
    try:
        # First, try to find existing label
        labels = service.users().labels().list(userId=USER_ID).execute().get('labels', [])
        
        for label in labels:
            if label['name'].lower() == label_name.lower():
                logger.debug(f"Found existing label '{label_name}' with ID {label['id']}")
                return label['id']
        
        # Create new label if not found
        logger.info(f"Creating new label '{label_name}'")
        label_object = {
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
        
        created_label = service.users().labels().create(
            userId=USER_ID, 
            body=label_object
        ).execute()
        
        logger.info(f"Created label '{label_name}' with ID {created_label['id']}")
        return created_label['id']
        
    except Exception as e:
        logger.error(f"Failed to get or create label '{label_name}': {e}")
        raise ActionError(f"Label operation failed: {e}")


def validate_action(action: str) -> bool:
    """
    Validate if an action is supported.
    
    Args:
        action: Action string to validate
        
    Returns:
        True if action is supported, False otherwise
    """
    if action in SUPPORTED_ACTIONS:
        return True
    
    if action.startswith(MOVE_ACTION_PREFIX):
        label_name = action.split(':', 1)[1] if ':' in action else ''
        return bool(label_name)
    
    return False


def get_supported_actions() -> List[str]:
    """
    Get list of all supported actions.
    
    Returns:
        List of supported action strings
    """
    return SUPPORTED_ACTIONS + [f"{MOVE_ACTION_PREFIX}label_name"]
