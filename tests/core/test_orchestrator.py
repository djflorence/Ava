"""
Tests for system orchestrator.
"""
import asyncio
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from src.ava.core.orchestrator import SystemOrchestrator
from src.ava.memory.models import EmotionalContext

@pytest.fixture
def memory_manager():
    """Create mock memory manager."""
    manager = AsyncMock()
    manager.get_memories.return_value = []
    manager.initialize = AsyncMock()
    return manager

@pytest.fixture
def emotional_system():
    """Create mock emotional system."""
    system = AsyncMock()
    system.get_current_state.return_value = EmotionalContext(
        primary="neutral",
        intensity=0.5,
        valence=0.0,
        arousal=0.5
    )
    system.initialize = AsyncMock()
    return system

@pytest.fixture
def personality_system():
    """Create mock personality system."""
    system = AsyncMock()
    system.personality_profile = MagicMock(development_stage="developing")
    system.last_update = datetime.now()
    system.update_personality = AsyncMock(return_value=True)
    system.get_personality_summary = AsyncMock(return_value={
        "traits": {},
        "development_stage": "developing"
    })
    return system

@pytest.fixture
def self_awareness():
    """Create mock self-awareness system."""
    system = AsyncMock()
    system.last_reflection = datetime.now()
    system.reflect = AsyncMock(return_value=True)
    return system

@pytest.fixture
def memory_consolidation():
    """Create mock memory consolidation system."""
    system = AsyncMock()
    system.last_consolidation = datetime.now()
    system.consolidate_memories = AsyncMock(return_value=True)
    return system

@pytest.fixture
def openai_client():
    """Create mock OpenAI client."""
    client = AsyncMock()
    return client

@pytest.fixture
def orchestrator(tmp_path, monkeypatch):
    """Create system orchestrator with mocked components."""
    # Mock component creation
    with patch("src.ava.core.orchestrator.MemoryManager") as mock_mm, \
         patch("src.ava.core.orchestrator.EmotionalIntelligence") as mock_ei, \
         patch("src.ava.core.orchestrator.PersonalityDevelopment") as mock_pd, \
         patch("src.ava.core.orchestrator.SelfAwareness") as mock_sa, \
         patch("src.ava.core.orchestrator.MemoryConsolidation") as mock_mc, \
         patch("src.ava.core.orchestrator.OpenAIClient") as mock_oc:

        # Configure mocks
        mock_mm.return_value = AsyncMock()
        mock_ei.return_value = AsyncMock()
        mock_pd.return_value = AsyncMock()
        mock_sa.return_value = AsyncMock()
        mock_mc.return_value = AsyncMock()
        mock_oc.return_value = AsyncMock()

        orchestrator = SystemOrchestrator(
            base_dir=tmp_path,
            openai_api_key="test-key"
        )

        return orchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator):
    """Test orchestrator initialization."""
    assert orchestrator.is_running == False
    assert isinstance(orchestrator.last_health_check, datetime)
    assert len(orchestrator.tasks) == 0

@pytest.mark.asyncio
async def test_start_and_shutdown(orchestrator):
    """Test starting and shutting down the orchestrator."""
    # Start systems
    await orchestrator.start()
    assert orchestrator.is_running == True
    assert len(orchestrator.tasks) == 4  # Four background tasks

    # Shutdown systems
    await orchestrator.shutdown()
    assert orchestrator.is_running == False
    assert all(task.cancelled() for task in orchestrator.tasks)

@pytest.mark.asyncio
async def test_save_final_states(orchestrator):
    """Test saving final states during shutdown."""
    await orchestrator.start()

    # Mock current state
    orchestrator.emotional_system.get_current_state.return_value = EmotionalContext(
        primary="calm",
        intensity=0.6,
        valence=0.3
    )

    await orchestrator.shutdown()

    # Verify final states were saved
    orchestrator.memory_manager.add_memory.assert_called_once()
    orchestrator.self_awareness.reflect.assert_called_once_with(force=True)
    orchestrator.personality_system.update_personality.assert_called_once_with(force=True)
    orchestrator.memory_consolidation.consolidate_memories.assert_called_once_with(force=True)

@pytest.mark.asyncio
async def test_periodic_tasks(orchestrator):
    """Test periodic task execution."""
    await orchestrator.start()

    # Wait for a short period to allow tasks to run
    await asyncio.sleep(0.1)

    # Verify tasks were started
    assert orchestrator.memory_consolidation.consolidate_memories.called
    assert orchestrator.self_awareness.reflect.called
    assert orchestrator.personality_system.update_personality.called

    await orchestrator.shutdown()

@pytest.mark.asyncio
async def test_health_monitoring(orchestrator):
    """Test health monitoring system."""
    initial_check = orchestrator.last_health_check

    await orchestrator._check_system_health()

    assert orchestrator.last_health_check > initial_check
    orchestrator.memory_manager.get_memories.assert_called_once()
    orchestrator.emotional_system.get_current_state.assert_called_once()
    orchestrator.personality_system.get_personality_summary.assert_called_once()

@pytest.mark.asyncio
async def test_get_system_status(orchestrator):
    """Test getting system status."""
    status = await orchestrator.get_system_status()

    assert isinstance(status, dict)
    assert "is_running" in status
    assert "last_health_check" in status
    assert "memory_system" in status
    assert "emotional_system" in status
    assert "personality_system" in status
    assert "self_awareness" in status

@pytest.mark.asyncio
async def test_error_handling(orchestrator):
    """Test error handling in background tasks."""
    # Simulate error in memory consolidation
    orchestrator.memory_consolidation.consolidate_memories.side_effect = Exception("Test error")

    # Start systems
    await orchestrator.start()

    # Wait for a short period
    await asyncio.sleep(0.1)

    # System should still be running despite the error
    assert orchestrator.is_running == True

    await orchestrator.shutdown()

@pytest.mark.asyncio
async def test_startup_failure_handling(orchestrator):
    """Test handling of startup failures."""
    # Simulate initialization failure
    orchestrator.memory_manager.initialize.side_effect = Exception("Initialization failed")

    # Attempt to start systems
    with pytest.raises(Exception):
        await orchestrator.start()

    # Verify system was shut down
    assert orchestrator.is_running == False
    assert len(orchestrator.tasks) == 0
