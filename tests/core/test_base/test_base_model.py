"""
Tests for base model functionality.
"""
import pytest
from datetime import datetime

from src.ava.core.models.base import AvaBaseModel

def test_base_model_creation():
    """Test base model creation and defaults."""
    model = AvaBaseModel()
    assert isinstance(model.created_at, datetime)
    assert model.updated_at is None

def test_base_model_serialization():
    """Test model serialization with datetime handling."""
    model = AvaBaseModel(
        created_at=datetime(2025, 1, 1, 12, 0, 0)
    )
    data = model.model_dump()
    assert data["created_at"] == "2025-01-01T12:00:00"
    assert data["updated_at"] is None

def test_base_model_deserialization():
    """Test model deserialization with datetime handling."""
    data = {
        "created_at": "2025-01-01T12:00:00",
        "updated_at": None
    }
    model = AvaBaseModel.model_validate(data)
    assert isinstance(model.created_at, datetime)
    assert model.created_at.year == 2025
    assert model.updated_at is None

def test_update_timestamp():
    """Test timestamp update functionality."""
    model = AvaBaseModel()
    assert model.updated_at is None
    model.update_timestamp()
    assert isinstance(model.updated_at, datetime)
    assert abs((model.updated_at - datetime.now()).total_seconds()) < 1
