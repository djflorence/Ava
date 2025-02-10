"""
Tests for CLI module.
"""
import pytest
from click.testing import CliRunner

from src.ava.cli import cli, chat, analyze

@pytest.fixture
def runner():
    """Fixture for CLI runner."""
    return CliRunner()

def test_cli_help(runner):
    """Test CLI help command."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Ava - An autonomous AI being" in result.output

def test_analyze_command(runner):
    """Test analyze command."""
    test_text = "I'm really happy about this!"
    result = runner.invoke(analyze, [test_text])

    assert result.exit_code == 0
    assert "Emotional Context" in result.output
    assert "Primary Emotion" in result.output
    assert "joy" in result.output.lower()
    assert "Intensity" in result.output
    assert "Valence" in result.output

def test_analyze_command_error(runner):
    """Test analyze command with empty input."""
    result = runner.invoke(analyze, [""])
    assert result.exit_code != 0
    assert "Error" in result.output

def test_chat_command_exit(runner):
    """Test chat command exit."""
    result = runner.invoke(chat, input="exit\n")

    assert result.exit_code == 0
    assert "Welcome to Ava" in result.output
    assert "Goodbye" in result.output

def test_chat_command_interaction(runner):
    """Test chat command interaction."""
    user_input = "I'm feeling great today!\nexit\n"
    result = runner.invoke(chat, input=user_input)

    assert result.exit_code == 0
    assert "Welcome to Ava" in result.output
    assert "Emotional Analysis" in result.output
    assert "Primary Emotion" in result.output
    assert "Goodbye" in result.output

def test_chat_command_interrupt(runner):
    """Test chat command keyboard interrupt."""
    def interrupt():
        raise KeyboardInterrupt

    result = runner.invoke(chat, input=interrupt)

    assert result.exit_code == 0
    assert "Chat session interrupted" in result.output

def test_chat_command_model_option(runner):
    """Test chat command with model option."""
    result = runner.invoke(
        chat,
        ["--model", "bert-base-uncased"],
        input="exit\n"
    )

    assert result.exit_code == 0
    assert "Welcome to Ava" in result.output

def test_cli_error_handling(runner):
    """Test CLI error handling."""
    # Test invalid command
    result = runner.invoke(cli, ["invalid"])
    assert result.exit_code != 0

    # Test invalid option
    result = runner.invoke(chat, ["--invalid"])
    assert result.exit_code != 0
