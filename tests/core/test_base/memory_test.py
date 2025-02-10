"""
Base test class for memory-related components.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Type, TypeVar
import pytest

from src.ava.memory.manager import MemoryManager
from src.ava.memory.models import Memory, MemoryMetadata
from src.ava.types import MemoryType
from . import AvaBaseTest

M = TypeVar('M', bound=Memory)

class MemoryComponentTest(AvaBaseTest[MemoryManager]):
    """Base class for testing memory-related components."""

    memory_class: Type[M]
    component_class = MemoryManager

    async def create_test_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.PERSONAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> M:
        """Create a test memory instance."""
        if not hasattr(self, 'memory_class'):
            raise NotImplementedError("memory_class must be defined in the test class")

        metadata = metadata or {}
        memory = self.memory_class(
            content=content,
            type=memory_type.value,
            metadata=MemoryMetadata(**metadata).model_dump()
        )
        return memory

    async def store_test_memories(
        self,
        component: MemoryManager,
        memories: List[M]
    ) -> List[str]:
        """Store multiple test memories and return their IDs."""
        memory_ids = []
        for memory in memories:
            await component.store_memory(memory)
            memory_ids.append(memory.id)
        return memory_ids

    async def verify_memory_retrieval(
        self,
        component: MemoryManager,
        memory_id: str,
        expected_content: str,
        expected_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Verify that a memory can be retrieved with expected content and metadata."""
        memory = component.get_memory_by_id(memory_id)
        assert memory is not None, f"Memory {memory_id} not found"
        assert memory.content == expected_content, \
            f"Memory content mismatch: expected {expected_content}, got {memory.content}"

        if expected_metadata:
            actual_metadata = memory.metadata
            for key, value in expected_metadata.items():
                assert key in actual_metadata, f"Missing metadata key: {key}"
                assert actual_metadata[key] == value, \
                    f"Metadata value mismatch for {key}: expected {value}, got {actual_metadata[key]}"

    async def verify_memory_search(
        self,
        component: MemoryManager,
        query: str,
        expected_count: int,
        min_similarity: float = 0.0
    ) -> List[Memory]:
        """Verify memory search results."""
        results = await component.search_memories(query, min_similarity=min_similarity)
        assert len(results) == expected_count, \
            f"Search result count mismatch: expected {expected_count}, got {len(results)}"
        return [memory for memory, _ in results]

    def get_test_memory_path(self, memory_type: MemoryType) -> Path:
        """Get the path for test memory files of a specific type."""
        return self.test_config.memory_dir / memory_type.value

    async def cleanup_test_memories(self, component: MemoryManager, memory_ids: List[str]) -> None:
        """Clean up test memories after tests."""
        for memory_id in memory_ids:
            memory = component.get_memory_by_id(memory_id)
            if memory:
                memory_path = self.get_test_memory_path(MemoryType(memory.type)) / f"{memory_id}.json"
                if memory_path.exists():
                    memory_path.unlink()
