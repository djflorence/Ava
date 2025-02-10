"""
Base test class for emotional-related components.
"""
from typing import Dict, Any, List, Optional
import pytest
from datetime import datetime, timedelta

from src.ava.emotional.emotional_intelligence import EmotionalIntelligence
from src.ava.emotional.models.emotional_state import EmotionalState
from src.ava.memory.models.emotional_context import EmotionalContext
from . import AvaBaseTest

class EmotionalComponentTest(AvaBaseTest[EmotionalIntelligence]):
    """Base class for testing emotional-related components."""

    component_class = EmotionalIntelligence

    async def create_test_emotional_state(
        self,
        primary_emotion: str,
        intensity: float = 0.5,
        valence: float = 0.0,
        arousal: float = 0.5,
        context: Optional[Dict[str, Any]] = None
    ) -> EmotionalState:
        """Create a test emotional state."""
        return EmotionalState(
            primary=primary_emotion,
            intensity=intensity,
            valence=valence,
            arousal=arousal,
            context=context or {}
        )

    async def verify_emotional_state(
        self,
        component: EmotionalIntelligence,
        state: EmotionalState,
        expected_values: Dict[str, Any],
        tolerance: float = 0.1
    ) -> None:
        """Verify emotional state values."""
        for key, expected_value in expected_values.items():
            actual_value = getattr(state, key)
            if isinstance(expected_value, (int, float)):
                assert abs(actual_value - expected_value) <= tolerance, \
                    f"Value mismatch for {key}: expected {expected_value}, got {actual_value}"
            else:
                assert actual_value == expected_value, \
                    f"Value mismatch for {key}: expected {expected_value}, got {actual_value}"

    async def verify_emotional_transition(
        self,
        component: EmotionalIntelligence,
        from_state: EmotionalState,
        to_state: EmotionalState,
        expected_changes: Dict[str, Any],
        tolerance: float = 0.1
    ) -> None:
        """Verify emotional state transition."""
        for key, expected_change in expected_changes.items():
            from_value = getattr(from_state, key)
            to_value = getattr(to_state, key)
            actual_change = to_value - from_value if isinstance(to_value, (int, float)) else None

            if actual_change is not None:
                assert abs(actual_change - expected_change) <= tolerance, \
                    f"Change mismatch for {key}: expected {expected_change}, got {actual_change}"

    async def create_emotional_sequence(
        self,
        emotions: List[str],
        time_interval: timedelta = timedelta(minutes=5)
    ) -> List[EmotionalState]:
        """Create a sequence of emotional states."""
        states = []
        base_time = datetime.now()

        for i, emotion in enumerate(emotions):
            state = await self.create_test_emotional_state(
                primary_emotion=emotion,
                intensity=0.5 + (i * 0.1),
                valence=(-0.5 + (i * 0.2)),
                arousal=0.3 + (i * 0.15)
            )
            state.timestamp = (base_time + (time_interval * i)).isoformat()
            states.append(state)

        return states

    async def verify_emotional_pattern(
        self,
        component: EmotionalIntelligence,
        pattern: Dict[str, Any],
        states: List[EmotionalState],
        tolerance: float = 0.1
    ) -> None:
        """Verify emotional pattern in a sequence of states."""
        if 'trend' in pattern:
            values = [getattr(state, pattern['attribute']) for state in states]
            trend = sum(b - a for a, b in zip(values, values[1:])) / (len(values) - 1)
            assert abs(trend - pattern['trend']) <= tolerance, \
                f"Trend mismatch: expected {pattern['trend']}, got {trend}"

        if 'frequency' in pattern:
            emotion = pattern['emotion']
            count = sum(1 for state in states if state.primary == emotion)
            expected_freq = pattern['frequency']
            actual_freq = count / len(states)
            assert abs(actual_freq - expected_freq) <= tolerance, \
                f"Frequency mismatch for {emotion}: expected {expected_freq}, got {actual_freq}"

    def create_test_emotional_context(
        self,
        primary_emotion: str,
        intensity: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EmotionalContext:
        """Create a test emotional context."""
        return EmotionalContext(
            primary=primary_emotion,
            intensity=intensity,
            metadata=metadata or {}
        )
