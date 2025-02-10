"""
Tests for logging module.
"""
import logging
from pathlib import Path

import pytest

from src.ava.utils.logging import setup_logging, get_logger

def test_setup_logging_console_only():
    """Test logging setup with console output only."""
    setup_logging(level="DEBUG")

    logger = logging.getLogger("ava")
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.Handler)

def test_setup_logging_with_file(tmp_path):
    """Test logging setup with both console and file output."""
    log_dir = tmp_path / "logs"
    setup_logging(log_dir=log_dir, level="INFO")

    logger = logging.getLogger("ava")
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 2

    # Verify log directory and file creation
    assert log_dir.exists()
    log_files = list(log_dir.glob("ava_*.log"))
    assert len(log_files) == 1

    # Test logging
    test_message = "Test log message"
    logger.info(test_message)

    # Verify message in log file
    log_content = log_files[0].read_text()
    assert test_message in log_content

def test_get_logger():
    """Test getting a logger for a module."""
    logger = get_logger("test_module")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "ava.test_module"

    # Test logging levels
    assert logger.isEnabledFor(logging.INFO)
    assert logger.isEnabledFor(logging.ERROR)

def test_logging_formatting(tmp_path, caplog):
    """Test log message formatting."""
    log_dir = tmp_path / "logs"
    setup_logging(log_dir=log_dir, level="DEBUG", rich_logging=False)

    logger = get_logger("test_format")
    test_message = "Test formatting"
    logger.info(test_message)

    # Check console output format
    for record in caplog.records:
        assert record.levelname in record.message
        assert "test_format" in record.message

    # Check file output format
    log_files = list(log_dir.glob("ava_*.log"))
    log_content = log_files[0].read_text()
    assert "INFO" in log_content
    assert "test_format" in log_content
    assert test_message in log_content

def test_rich_logging_setup():
    """Test rich logging setup."""
    setup_logging(level="INFO", rich_logging=True)

    logger = logging.getLogger("ava")
    handler = logger.handlers[0]

    # Verify rich handler configuration
    assert "RichHandler" in handler.__class__.__name__
    assert handler.show_time
    assert handler.show_path
    assert handler.rich_tracebacks

def test_logging_hierarchy():
    """Test logging hierarchy and level inheritance."""
    setup_logging(level="WARNING")

    parent_logger = get_logger("parent")
    child_logger = get_logger("parent.child")

    assert child_logger.parent == parent_logger
    assert child_logger.level == logging.WARNING

    # Test level override
    child_logger.setLevel(logging.DEBUG)
    assert child_logger.level == logging.DEBUG
    assert child_logger.getEffectiveLevel() == logging.DEBUG
