"""Tests for the primary conversation handler."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.ava.core.conversation_handler import ConversationHandler, ConversationContext
from src.ava.memory.models import Memory, EmotionalContext
from src.ava.llm.openai_integration import Message

@pytest.fixture
def mock_memory_manager():
    """Mock memory manager fixture."""
    manager = AsyncMock()
    manager.get_relevant_memories.return_value = []
    manager.add_memory.return_value = None
    return manager

@pytest.fixture
def mock_emotional_system():
    """Mock emotional system fixture."""
    system = AsyncMock()
    system.analyze_text.return_value = EmotionalContext(
        primary="neutral",
        intensity=0.5,
        valence=0.0,
        arousal=0.0
    )
    system.update_emotional_state.return_value = None
    return system

@pytest.fixture
def mock_personality_system():
    """Mock personality system fixture."""
    system = AsyncMock()
    system.get_personality_summary.return_value = {
        "traits": {
            "openness": 0.7,
            "conscientiousness": 0.8
        }
    }
    return system

@pytest.fixture
def mock_self_awareness():
    """Mock self-awareness system fixture."""
    return AsyncMock()

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client fixture."""
    client = AsyncMock()
    client.generate_response.return_value = "Test response"
    return client

@pytest.fixture
def conversation_handler(
    mock_memory_manager,
    mock_emotional_system,
    mock_personality_system,
    mock_self_awareness,
    mock_openai_client
):
    """Conversation handler fixture with mocked dependencies."""
    return ConversationHandler(
        memory_manager=mock_memory_manager,
        emotional_system=mock_emotional_system,
        personality_system=mock_personality_system,
        self_awareness=mock_self_awareness,
        openai_client=mock_openai_client
    )

@pytest.mark.asyncio
async def test_process_message(conversation_handler, mock_openai_client):
    """Test basic message processing."""
    response = await conversation_handler.process_message("Hello")

    assert response == "Test response"
    assert len(conversation_handler.conversation_history) == 1
    assert conversation_handler.last_interaction is not None

@pytest.mark.asyncio
async def test_process_message_with_memory(
    conversation_handler,
    mock_memory_manager
):
    """Test message processing with relevant memories."""
    memory = Memory(
        id="test",
        content="Previous interaction",
        memory_type="personal"
    )
    mock_memory_manager.get_relevant_memories.return_value = [memory]

    response = await conversation_handler.process_message("Hello")

    assert response == "Test response"
    mock_memory_manager.add_memory.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_with_emotion(
    conversation_handler,
    mock_emotional_system
):
    """Test message processing with emotional context."""
    emotional_context = EmotionalContext(
        primary="joy",
        intensity=0.8,
        valence=0.7,
        arousal=0.6
    )
    mock_emotional_system.analyze_text.return_value = emotional_context

    response = await conversation_handler.process_message("I'm happy!")

    assert response == "Test response"
    mock_emotional_system.update_emotional_state.assert_called_once()

@pytest.mark.asyncio
async def test_error_handling(conversation_handler, mock_openai_client):
    """Test error handling during message processing."""
    mock_openai_client.generate_response.side_effect = Exception("Test error")

    response = await conversation_handler.process_message("Hello")

    assert "I apologize" in response
    assert "try again" in response

@pytest.mark.asyncio
async def test_conversation_context_creation(conversation_handler):
    """Test conversation context model creation."""
    context = ConversationContext(
        user_input="test",
        emotional_state=EmotionalContext(primary="neutral"),
        personality_state={"traits": {}},
        conversation_history=[]
    )

    assert context.user_input == "test"
    assert context.emotional_state.primary == "neutral"
    assert isinstance(context.timestamp, datetime)

@pytest.mark.asyncio
async def test_message_preparation(conversation_handler):
    """Test LLM message preparation."""
    context = ConversationContext(
        user_input="test",
        emotional_state=EmotionalContext(primary="neutral"),
        personality_state={"traits": {"openness": 0.7}},
        conversation_history=[]
    )

    messages = conversation_handler._prepare_messages(context)

    assert len(messages) > 0
    assert isinstance(messages[0], Message)
    assert "You are Ava" in messages[0].content

@pytest.mark.asyncio
async def test_conversation_end(conversation_handler, mock_memory_manager):
    """Test conversation end handling."""
    # Add some conversation history
    await conversation_handler.process_message("Hello")
    await conversation_handler.process_message("How are you?")

    await conversation_handler.end_conversation()

    assert len(conversation_handler.conversation_history) == 0
    assert conversation_handler.last_interaction is None
    mock_memory_manager.add_memory.assert_called()

@pytest.mark.asyncio
async def test_conversation_summary(conversation_handler, mock_openai_client):
    """Test conversation summary generation."""
    # Add conversation history
    conversation_handler.conversation_history = [
        {
            "user_input": "Hello",
            "response": "Hi!",
            "timestamp": datetime.now().isoformat()
        }
    ]

    mock_openai_client.generate_response.return_value = "Summary of conversation"

    summary = await conversation_handler._generate_conversation_summary()

    assert summary == "Summary of conversation"
    mock_openai_client.generate_response.assert_called_once()
