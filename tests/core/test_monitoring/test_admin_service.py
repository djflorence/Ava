"""
Tests for the admin service API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from ava.api.admin_service import app
from ava.memory.models import Memory as CoreMemory

# Mark all tests as async
pytestmark = pytest.mark.asyncio

@pytest.fixture
def test_client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def mock_memory_manager():
    """Create a mock memory manager."""
    mock = AsyncMock()
    # Setup mock memory for stats
    mock_memory = {
        "id": "test1",
        "type": "core",
        "content": "Test content",
        "importance": 0.5,
        "themes": ["test"],
        "last_accessed": datetime.now().isoformat(),
        "access_count": 10
    }
    mock.get_memories.return_value = [mock_memory]
    mock.get_memory.return_value = mock_memory
    mock.get_recent_errors.return_value = [{
        "message": "Test error",
        "source": "test",
        "severity": "info",
        "timestamp": datetime.now().isoformat()
    }]
    mock._save_memory = AsyncMock()
    return mock

@pytest.fixture
def mock_memory_migrator():
    """Create a mock memory migrator."""
    mock = AsyncMock()
    mock.create_backup.return_value = "test-backup-id"
    mock.list_backups.return_value = [{
        "id": "test-backup-id",
        "timestamp": "2024-01-01T00:00:00",
        "description": "Test backup"
    }]
    mock.restore_from_backup.return_value = True
    mock.get_last_backup_time.return_value = datetime.now().isoformat()
    return mock

async def test_get_admin_stats(test_client, mock_memory_manager, mock_memory_migrator):
    """Test getting admin stats."""
    with patch("ava.api.admin_service.memory_manager", mock_memory_manager), \
         patch("ava.api.admin_service.memory_migrator", mock_memory_migrator):
        response = test_client.get("/admin/stats")
        assert response.status_code == 200
        data = response.json()
        assert "memory_stats" in data
        assert "health_status" in data
        assert "timestamp" in data

async def test_create_backup(test_client, mock_memory_migrator):
    """Test creating a backup."""
    with patch("ava.api.admin_service.memory_migrator", mock_memory_migrator):
        response = test_client.post(
            "/admin/backup",
            json={"description": "Test backup"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["backup_id"] == "test-backup-id"

async def test_restore_backup(test_client, mock_memory_migrator):
    """Test restoring from a backup."""
    with patch("ava.api.admin_service.memory_migrator", mock_memory_migrator):
        response = test_client.post(
            "/admin/restore",
            json={"backup_id": "test-backup-id"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

async def test_list_backups(test_client, mock_memory_migrator):
    """Test listing backups."""
    with patch("ava.api.admin_service.memory_migrator", mock_memory_migrator):
        response = test_client.get("/admin/backups")
        assert response.status_code == 200
        data = response.json()
        assert "backups" in data
        assert len(data["backups"]) == 1
        assert data["backups"][0]["id"] == "test-backup-id"

async def test_edit_memory(test_client, mock_memory_manager, mock_memory_migrator):
    """Test editing a memory."""
    with patch("ava.api.admin_service.memory_manager", mock_memory_manager), \
         patch("ava.api.admin_service.memory_migrator", mock_memory_migrator):
        response = test_client.post(
            "/admin/memory/edit",
            json={
                "memory_id": "test1",
                "content": "Updated content",
                "importance": 0.8,
                "themes": ["test", "updated"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["memory_id"] == "test1"
        assert data["backup_id"] == "test-backup-id"

async def test_get_memory_access_stats(test_client, mock_memory_manager):
    """Test getting memory access statistics."""
    with patch("ava.api.admin_service.memory_manager", mock_memory_manager):
        response = test_client.get("/admin/memory/access-stats")
        assert response.status_code == 200
        data = response.json()
        assert "access_stats" in data
        assert "timestamp" in data
        access_stats = data["access_stats"]
        assert "most_accessed" in access_stats
        assert "recent_access" in access_stats
        assert "importance_distribution" in access_stats

async def test_get_error_log(test_client, mock_memory_manager):
    """Test getting error log."""
    with patch("ava.api.admin_service.memory_manager", mock_memory_manager):
        response = test_client.get("/admin/errors")
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert "timestamp" in data
        assert len(data["errors"]) == 1
        error = data["errors"][0]
        assert error["message"] == "Test error"
        assert error["source"] == "test"
        assert error["severity"] == "info"

async def test_error_handling(test_client, mock_memory_manager):
    """Test error handling in endpoints."""
    with patch("ava.api.admin_service.memory_manager", mock_memory_manager):
        # Test error in get_admin_stats
        mock_memory_manager.get_memories.side_effect = Exception("Test error")
        response = test_client.get("/admin/stats")
        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "Test error"
