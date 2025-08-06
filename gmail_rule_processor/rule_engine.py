"""
Rule engine for processing email rules.

This module handles the evaluation of email rules and application of actions
based on rule conditions.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from config import DEFAULT_RULES_FILE, SUPPORTED_FIELDS, SUPPORTED_PREDICATES
from database import get_all_emails, DatabaseError
from actions import perform_actions

logger = logging.getLogger(__name__)


class RuleEngineError(Exception):
    """Custom exception for rule engine errors."""
    pass


def load_rules(filename: str = DEFAULT_RULES_FILE) -> Dict[str, Any]:
    """
    Load rules from a JSON file.
    
    Args:
        filename: Path to the rules JSON file
        
    Returns:
        Dictionary containing rule configuration
        
    Raises:
        RuleEngineError: If rules file cannot be loaded or is invalid
    """
    try:
        with open(filename, 'r') as f:
            rules = json.load(f)
        
        # Validate rules structure
        if not isinstance(rules, dict):
            raise RuleEngineError("Rules file must contain a JSON object")
        
        if 'rules' not in rules:
            raise RuleEngineError("Rules file must contain a 'rules' array")
        
        if 'actions' not in rules:
            raise RuleEngineError("Rules file must contain an 'actions' array")
        
        logger.info(f"Loaded rules from {filename}")
        return rules
        
    except FileNotFoundError:
        logger.error(f"Rules file not found: {filename}")
        raise RuleEngineError(f"Rules file not found: {filename}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in rules file {filename}: {e}")
        raise RuleEngineError(f"Invalid JSON in rules file: {e}")
    except Exception as e:
        logger.error(f"Failed to load rules from {filename}: {e}")
        raise RuleEngineError(f"Failed to load rules: {e}")


def get_emails():
    """
    Get all emails from the database.
    
    Returns:
        List of email dictionaries
    """
    return get_all_emails()


def validate_condition(condition: Dict[str, Any]) -> None:
    """
    Validate a rule condition.
    
    Args:
        condition: Dictionary containing field, predicate, and value
        
    Raises:
        RuleEngineError: If condition is invalid
    """
    required_fields = ['field', 'predicate', 'value']
    for field in required_fields:
        if field not in condition:
            raise RuleEngineError(f"Condition missing required field: {field}")
    
    field = condition['field']
    predicate = condition['predicate']
    value = condition['value']
    
    if field not in SUPPORTED_FIELDS:
        raise RuleEngineError(f"Unsupported field: {field}")
    
    if predicate not in SUPPORTED_PREDICATES:
        raise RuleEngineError(f"Unsupported predicate: {predicate}")
    
    if not value:
        raise RuleEngineError("Condition value cannot be empty")


def evaluate_condition(email: Dict[str, Any], condition: Dict[str, Any]) -> bool:
    """
    Evaluate if an email matches a condition.
    
    Args:
        email: Email data dictionary
        condition: Rule condition dictionary
        
    Returns:
        True if email matches condition, False otherwise
    """
    try:
        validate_condition(condition)
        
        field = condition["field"]
        predicate = condition["predicate"]
        value = condition["value"]
        
        email_value = email.get(field)
        
        # Handle date-based conditions
        if field == "received_at":
            return _evaluate_date_condition(email_value, predicate, value)
        
        # Handle boolean conditions
        if field == "is_read":
            return _evaluate_boolean_condition(email_value, predicate, value)
        
        # Handle text-based conditions
        if not isinstance(email_value, str):
            return False
        
        return _evaluate_text_condition(email_value, predicate, value)
        
    except RuleEngineError:
        raise
    except Exception as e:
        logger.error(f"Error evaluating condition: {e}")
        return False


def _evaluate_date_condition(email_value: str, predicate: str, value: str) -> bool:
    """
    Evaluate date-based conditions.
    
    Args:
        email_value: Email date value
        predicate: Comparison predicate
        value: Days value as string
        
    Returns:
        True if condition is met, False otherwise
    """
    try:
        email_date = datetime.fromisoformat(email_value)
        days = int(value)
        now = datetime.now(timezone.utc)
        
        if predicate == "less_than_days":
            return email_date > now - timedelta(days=days)
        elif predicate == "greater_than_days":
            return email_date < now - timedelta(days=days)
        else:
            return False
            
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid date value: {email_value}, error: {e}")
        return False


def _evaluate_boolean_condition(email_value: bool, predicate: str, value: str) -> bool:
    """
    Evaluate boolean conditions.
    
    Args:
        email_value: Email boolean value
        predicate: Comparison predicate
        value: Expected value as string
        
    Returns:
        True if condition is met, False otherwise
    """
    try:
        expected_value = value.lower() == 'true'
        
        if predicate == "equals":
            return email_value == expected_value
        elif predicate == "not_equals":
            return email_value != expected_value
        else:
            return False
            
    except Exception as e:
        logger.warning(f"Invalid boolean condition: {e}")
        return False


def _evaluate_text_condition(email_value: str, predicate: str, value: str) -> bool:
    """
    Evaluate text-based conditions.
    
    Args:
        email_value: Email text value
        predicate: Comparison predicate
        value: Comparison value
        
    Returns:
        True if condition is met, False otherwise
    """
    email_lower = email_value.lower()
    value_lower = value.lower()
    
    if predicate == "contains":
        return value_lower in email_lower
    elif predicate == "not_contains":
        return value_lower not in email_lower
    elif predicate == "equals":
        return email_lower == value_lower
    elif predicate == "not_equals":
        return email_lower != value_lower
    else:
        return False


def apply_rules(service, rule_file: str = DEFAULT_RULES_FILE) -> None:
    """
    Apply rules to emails and perform actions on matching emails.
    
    Args:
        service: Gmail API service object
        rule_file: Path to rules JSON file
    """
    try:
        # Load and validate rules
        ruleset = load_rules(rule_file)
        predicate_type = ruleset.get("predicate", "ALL")
        conditions = ruleset.get("rules", [])
        actions = ruleset.get("actions", [])
        
        # Validate conditions
        for condition in conditions:
            validate_condition(condition)
        
        # Get emails from database
        emails = get_emails()
        logger.info(f"Processing {len(emails)} emails with {len(conditions)} conditions")
        
        # Find matching emails
        matched_emails = _find_matching_emails(emails, conditions, predicate_type)
        
        logger.info(f"Found {len(matched_emails)} emails matching rules")
        
        # Perform actions on matched emails
        for email in matched_emails:
            try:
                perform_actions(service, email['id'], actions)
                logger.debug(f"Applied actions to email {email['id']}")
            except Exception as e:
                logger.error(f"Failed to apply actions to email {email['id']}: {e}")
                
    except (RuleEngineError, DatabaseError) as e:
        logger.error(f"Rule engine error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in rule engine: {e}")
        raise RuleEngineError(f"Rule engine failed: {e}")


def _find_matching_emails(emails: List[Dict[str, Any]], 
                         conditions: List[Dict[str, Any]], 
                         predicate_type: str) -> List[Dict[str, Any]]:
    """
    Find emails that match the given conditions.
    
    Args:
        emails: List of email dictionaries
        conditions: List of condition dictionaries
        predicate_type: "ALL" or "ANY" to determine matching logic
        
    Returns:
        List of matching email dictionaries
    """
    matched_emails = []
    
    for email in emails:
        results = [evaluate_condition(email, cond) for cond in conditions]
        
        if predicate_type == "ALL" and all(results):
            matched_emails.append(email)
        elif predicate_type == "ANY" and any(results):
            matched_emails.append(email)
    
    return matched_emails
