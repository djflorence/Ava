"""
Tests for datetime utilities.
"""
import pytest
from datetime import datetime

from src.ava.core.utils.datetime_utils import (
    serialize_datetime,
    deserialize_datetime,
    process_datetime_fields,
    get_current_datetime
)

def test_serialize_datetime():
    """Test datetime serialization."""
    # Test with valid datetime
    dt = datetime(2025, 1, 1, 12, 0, 0)
    assert serialize_datetime(dt) == "2025-01-01T12:00:00"

    # Test with None
    assert serialize_datetime(None) is None

def test_deserialize_datetime():
    """Test datetime deserialization."""
    # Test with valid ISO format string
    dt_str = "2025-01-01T12:00:00"
    dt = deserialize_datetime(dt_str)
    assert isinstance(dt, datetime)
    assert dt.year == 2025
    assert dt.month == 1
    assert dt.day == 1
    assert dt.hour == 12

    # Test with None
    assert deserialize_datetime(None) is None

    # Test with invalid string
    dt = deserialize_datetime("invalid")
    assert isinstance(dt, datetime)  # Should return current time

    # Test with existing datetime
    original_dt = datetime.now()
    assert deserialize_datetime(original_dt) == original_dt

def test_process_datetime_fields():
    """Test processing multiple datetime fields."""
    data = {
        "created_at": "2025-01-01T12:00:00",
        "updated_at": None,
        "other_field": "value"
    }

    processed = process_datetime_fields(data, ["created_at", "updated_at"])

    assert isinstance(processed["created_at"], datetime)
    assert isinstance(processed["updated_at"], datetime)
    assert processed["other_field"] == "value"

    # Test with missing fields
    data = {"other_field": "value"}
    processed = process_datetime_fields(data, ["created_at", "updated_at"])
    assert processed["other_field"] == "value"
    assert "created_at" not in processed

def test_get_current_datetime():
    """Test getting current datetime."""
    dt = get_current_datetime()
    assert isinstance(dt, datetime)
    assert dt.year == datetime.now().year
