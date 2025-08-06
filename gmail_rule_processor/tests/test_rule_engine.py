"""
Tests for the rule engine module.

This module contains unit tests for the rule evaluation functionality.
"""

import pytest
from datetime import datetime, timedelta, timezone
from rule_engine import evaluate_condition, validate_condition, RuleEngineError


@pytest.fixture
def sample_email():
    """Sample email data for testing."""
    return {
        "id": "123abc",
        "sender": "noreply@example.com",
        "subject": "Invoice for July",
        "body": "Please find attached your invoice",
        "received_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
        "label_ids": "INBOX",
        "is_read": False
    }


def test_subject_contains(sample_email):
    """Test subject contains condition."""
    condition = {"field": "subject", "predicate": "contains", "value": "invoice"}
    assert evaluate_condition(sample_email, condition) is True


def test_sender_equals(sample_email):
    condition = {"field": "sender", "predicate": "equals", "value": "noreply@example.com"}
    assert evaluate_condition(sample_email, condition) is True


def test_received_less_than_days(sample_email):
    condition = {"field": "received_at", "predicate": "less_than_days", "value": "3"}
    assert evaluate_condition(sample_email, condition) is True


def test_received_greater_than_days(sample_email):
    """Test received greater than days condition."""
    condition = {"field": "received_at", "predicate": "greater_than_days", "value": "1"}
    assert evaluate_condition(sample_email, condition) is True



def test_subject_not_contains(sample_email):
    condition = {"field": "subject", "predicate": "not_contains", "value": "payment"}
    assert evaluate_condition(sample_email, condition) is True


def test_sender_not_equals(sample_email):
    condition = {"field": "sender", "predicate": "not_equals", "value": "billing@example.com"}
    assert evaluate_condition(sample_email, condition) is True


def test_subject_not_contains_case_insensitive(sample_email):
    condition = {"field": "subject", "predicate": "not_contains", "value": "PAYMENT"}
    assert evaluate_condition(sample_email, condition) is True


def test_subject_equals_exact_match(sample_email):
    condition = {"field": "subject", "predicate": "equals", "value": "Invoice for July"}
    assert evaluate_condition(sample_email, condition) is True


def test_subject_not_equals_wrong_case(sample_email):
    condition = {"field": "subject", "predicate": "not_equals", "value": "invoice for july"}
    assert evaluate_condition(sample_email, condition) is False  # should be case-insensitive


def test_body_contains_keyword(sample_email):
    """Test body contains keyword."""
    condition = {"field": "body", "predicate": "contains", "value": "attached"}
    assert evaluate_condition(sample_email, condition) is True


def test_is_read_equals_true(sample_email):
    """Test is_read equals true."""
    condition = {"field": "is_read", "predicate": "equals", "value": "false"}
    assert evaluate_condition(sample_email, condition) is True


def test_is_read_not_equals_true(sample_email):
    """Test is_read not equals true."""
    condition = {"field": "is_read", "predicate": "not_equals", "value": "true"}
    assert evaluate_condition(sample_email, condition) is True


def test_invalid_field():
    """Test invalid field raises error."""
    condition = {"field": "invalid_field", "predicate": "contains", "value": "test"}
    with pytest.raises(RuleEngineError):
        evaluate_condition({}, condition)


def test_invalid_predicate():
    """Test invalid predicate raises error."""
    condition = {"field": "subject", "predicate": "invalid_predicate", "value": "test"}
    with pytest.raises(RuleEngineError):
        evaluate_condition({}, condition)


def test_empty_value():
    """Test empty value raises error."""
    condition = {"field": "subject", "predicate": "contains", "value": ""}
    with pytest.raises(RuleEngineError):
        evaluate_condition({}, condition)


def test_missing_field():
    """Test missing field raises error."""
    condition = {"predicate": "contains", "value": "test"}
    with pytest.raises(RuleEngineError):
        evaluate_condition({}, condition)


def test_missing_predicate():
    """Test missing predicate raises error."""
    condition = {"field": "subject", "value": "test"}
    with pytest.raises(RuleEngineError):
        evaluate_condition({}, condition)


def test_missing_value():
    """Test missing value raises error."""
    condition = {"field": "subject", "predicate": "contains"}
    with pytest.raises(RuleEngineError):
        evaluate_condition({}, condition)


def test_invalid_date_format():
    """Test invalid date format returns False."""
    email_data = {"received_at": "invalid_date"}
    condition = {"field": "received_at", "predicate": "less_than_days", "value": "1"}
    assert evaluate_condition(email_data, condition) is False


def test_none_email_value():
    """Test None email value returns False."""
    email_data = {"subject": None}
    condition = {"field": "subject", "predicate": "contains", "value": "test"}
    assert evaluate_condition(email_data, condition) is False

