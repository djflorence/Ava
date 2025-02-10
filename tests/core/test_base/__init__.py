"""
Base test classes and utilities.

This package provides the base test infrastructure for AVA's test suite, including:
- Base test classes
- Test fixtures
- Test utilities
- Mock data generation
"""

from typing import TypeVar, Type, Generic
from datetime import datetime
from pathlib import Path

import pytest
from pytest import FixtureRequest

from ...utils.mock_data import MockDataGenerator
from ...config.test_config import TestConfig

T = TypeVar('T')

class AvaBaseTest(Generic[T]):
    """Base class for all AVA test classes."""

    component_class: Type[T]
    test_data_generator = MockDataGenerator

    @pytest.fixture(autouse=True)
    def _setup_base(self, request: FixtureRequest, test_config: TestConfig):
        """Set up base test configuration."""
        self.test_config = test_config
        self.test_dir = Path(request.fspath).parent

    def get_test_file_path(self, filename: str) -> Path:
        """Get path to a test file."""
        return self.test_dir / filename

    def get_test_data_path(self, *paths: str) -> Path:
        """Get path to test data."""
        return self.test_config.base_dir.joinpath(*paths)

__all__ = [
    'AvaBaseTest',
    'MockDataGenerator',
]
