"""
Integration test for the Gmail Rule Processor.

This test verifies that the core functionality works correctly.
"""

import json
import tempfile
import os
from unittest.mock import Mock, patch
from rule_engine import evaluate_condition, validate_condition, RuleEngineError
from actions import validate_action, get_supported_actions


def test_rule_validation():
    """Test that rule validation works correctly."""
    # Valid condition
    valid_condition = {
        "field": "subject",
        "predicate": "contains",
        "value": "test"
    }
    validate_condition(valid_condition)  # Should not raise
    
    # Invalid condition - missing field
    invalid_condition = {
        "predicate": "contains",
        "value": "test"
    }
    try:
        validate_condition(invalid_condition)
        assert False, "Should have raised RuleEngineError"
    except RuleEngineError:
        pass
    
    # Invalid condition - empty value
    invalid_condition = {
        "field": "subject",
        "predicate": "contains",
        "value": ""
    }
    try:
        validate_condition(invalid_condition)
        assert False, "Should have raised RuleEngineError"
    except RuleEngineError:
        pass


def test_condition_evaluation():
    """Test that condition evaluation works correctly."""
    email = {
        "sender": "test@example.com",
        "subject": "Test Subject",
        "body": "Test message body",
        "received_at": "2023-01-01T00:00:00+00:00",
        "is_read": False
    }
    
    # Test contains
    condition = {"field": "subject", "predicate": "contains", "value": "Test"}
    assert evaluate_condition(email, condition) is True
    
    # Test not contains
    condition = {"field": "subject", "predicate": "not_contains", "value": "Invalid"}
    assert evaluate_condition(email, condition) is True
    
    # Test equals
    condition = {"field": "sender", "predicate": "equals", "value": "test@example.com"}
    assert evaluate_condition(email, condition) is True
    
    # Test not equals
    condition = {"field": "sender", "predicate": "not_equals", "value": "other@example.com"}
    assert evaluate_condition(email, condition) is True


def test_action_validation():
    """Test that action validation works correctly."""
    # Valid actions
    assert validate_action("mark_read") is True
    assert validate_action("mark_unread") is True
    assert validate_action("move:TestLabel") is True
    
    # Invalid actions
    assert validate_action("invalid_action") is False
    assert validate_action("move:") is False  # Empty label name


def test_supported_actions():
    """Test that supported actions are correctly listed."""
    actions = get_supported_actions()
    assert "mark_read" in actions
    assert "mark_unread" in actions
    assert "move:label_name" in actions


def test_rules_file_format():
    """Test that rules file format is correct."""
    rules = {
        "predicate": "ANY",
        "rules": [
            {
                "field": "subject",
                "predicate": "contains",
                "value": "test"
            }
        ],
        "actions": ["mark_read", "move:TestLabel"]
    }
    
    # Test that it can be serialized to JSON
    json_str = json.dumps(rules, indent=2)
    parsed_rules = json.loads(json_str)
    
    assert parsed_rules["predicate"] == "ANY"
    assert len(parsed_rules["rules"]) == 1
    assert len(parsed_rules["actions"]) == 2


def test_configuration():
    """Test that configuration is properly structured."""
    from config import (
        SUPPORTED_FIELDS, SUPPORTED_PREDICATES, 
        SUPPORTED_ACTIONS, MOVE_ACTION_PREFIX
    )
    
    # Check that all required fields are supported
    required_fields = ['sender', 'subject', 'body', 'received_at', 'is_read']
    for field in required_fields:
        assert field in SUPPORTED_FIELDS
    
    # Check that all required predicates are supported
    required_predicates = [
        'contains', 'not_contains', 'equals', 'not_equals',
        'less_than_days', 'greater_than_days'
    ]
    for predicate in required_predicates:
        assert predicate in SUPPORTED_PREDICATES
    
    # Check that all required actions are supported
    required_actions = ['mark_read', 'mark_unread']
    for action in required_actions:
        assert action in SUPPORTED_ACTIONS
    
    # Check move action prefix
    assert MOVE_ACTION_PREFIX == 'move:'


if __name__ == "__main__":
    print("Running integration tests...")
    
    test_rule_validation()
    print("✅ Rule validation tests passed")
    
    test_condition_evaluation()
    print("✅ Condition evaluation tests passed")
    
    test_action_validation()
    print("✅ Action validation tests passed")
    
    test_supported_actions()
    print("✅ Supported actions tests passed")
    
    test_rules_file_format()
    print("✅ Rules file format tests passed")
    
    test_configuration()
    print("✅ Configuration tests passed")
    
    print("\n🎉 All integration tests passed!")
    print("Your Gmail Rule Processor is ready for submission!") 
