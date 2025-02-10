"""Test configuration module."""
import os
from pathlib import Path

# Test OpenAI configuration
os.environ["OPENAI_API_KEY"] = "test_key_for_mock"

# Test paths
TEST_DIR = Path("test_data")
TEST_DIR.mkdir(exist_ok=True)

def cleanup():
    """Clean up test data."""
    import shutil
    shutil.rmtree(TEST_DIR, ignore_errors=True)

"""
Tests for configuration module.
"""
import pytest

from src.ava.config import Settings, EmotionalConfig, MemoryConfig

def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()

    assert settings.env == "development"
    assert not settings.debug
    assert isinstance(settings.base_dir, Path)
    assert isinstance(settings.data_dir, Path)
    assert settings.device == "cpu"
    assert settings.batch_size == 32

def test_emotional_config():
    """Test emotional configuration."""
    config = EmotionalConfig()

    assert config.sentiment_model == "distilbert-base-uncased-finetuned-sst-2-english"
    assert isinstance(config.decay_rates, dict)
    assert 0 < config.decay_rates["intensity"] < 1
    assert 0 < config.decay_rates["valence"] < 1
    assert 0 < config.decay_rates["arousal"] < 1
    assert 0 < config.confidence_threshold < 1

def test_memory_config():
    """Test memory configuration."""
    config = MemoryConfig()

    assert isinstance(config.memory_dir, Path)
    assert config.embedding_model == "sentence-transformers/all-mpnet-base-v2"
    assert config.max_memory_age > 0
    assert config.retrieval_limit > 0

def test_settings_environment_override(monkeypatch):
    """Test environment variable overrides."""
    # Set environment variables
    env_vars = {
        "AVA_ENV": "production",
        "AVA_DEBUG": "true",
        "AVA_DEVICE": "cuda",
        "AVA_BATCH_SIZE": "64",
        "AVA_EMOTIONAL__CONFIDENCE_THRESHOLD": "0.8",
        "AVA_MEMORY__MAX_MEMORY_AGE": "120"
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    settings = Settings()

    assert settings.env == "production"
    assert settings.debug is True
    assert settings.device == "cuda"
    assert settings.batch_size == 64
    assert settings.emotional.confidence_threshold == 0.8
    assert settings.memory.max_memory_age == 120

def test_settings_directory_creation(tmp_path):
    """Test directory creation on initialization."""
    settings = Settings(
        base_dir=tmp_path,
        data_dir=tmp_path / "data"
    )

    settings.setup_directories()

    assert settings.data_dir.exists()
    assert settings.memory.memory_dir.exists()
    assert (settings.data_dir / "logs").exists()
    assert (settings.data_dir / "models").exists()

def test_invalid_settings():
    """Test validation of invalid settings."""
    with pytest.raises(ValueError):
        EmotionalConfig(confidence_threshold=1.5)  # Should be <= 1.0

    with pytest.raises(ValueError):
        MemoryConfig(max_memory_age=-1)  # Should be positive

    with pytest.raises(ValueError):
        MemoryConfig(retrieval_limit=0)  # Should be positive
