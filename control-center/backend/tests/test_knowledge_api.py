"""
Tests for Knowledge Base API endpoints

Mock paths corrected by ARGUS QA Lead - 2025-12-28
Original mock paths (services.kb_integration.*) were non-existent.
Actual implementation uses inline functions in api.knowledge module.
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from datetime import datetime


class TestKnowledgeBaseAPI:
    """Test knowledge base integration endpoints"""

    def test_get_recent_kb_files(self, test_client):
        """Test getting recently modified knowledge base files"""
        mock_files = [
            {
                "path": "C:/kb/test.md",
                "name": "test.md",
                "agent": "character-pipeline",
                "size": 1024,
                "modified": "2025-11-07T09:00:00",
                "category": "comfyui-workflows"
            }
        ]

        with patch('api.knowledge.scan_kb_files', return_value=mock_files):
            response = test_client.get("/api/knowledge/recent?limit=10")

            assert response.status_code == 200
            data = response.json()

            assert "files" in data
            assert data["count"] >= 0

    def test_get_kb_stats(self, test_client):
        """Test knowledge base statistics"""
        mock_creator_db = {
            "metadata": {"total_creators": 38},
            "creators": []
        }
        mock_files = [
            {"path": "test.md", "agent": "character-pipeline", "size": 1024, "modified": "2025-11-07T09:00:00"}
        ]

        with patch('api.knowledge.load_creator_database', return_value=mock_creator_db), \
             patch('api.knowledge.scan_kb_files', return_value=mock_files):
            response = test_client.get("/api/knowledge/stats")

            assert response.status_code == 200
            data = response.json()

            assert "total_creators" in data
            assert "total_files" in data

    def test_get_kb_files_list(self, test_client):
        """Test listing knowledge base files with pagination"""
        mock_files = [
            {
                "path": "C:/kb/file1.md",
                "name": "file1.md",
                "agent": "art-director",
                "size": 512,
                "modified": "2025-11-07T10:00:00",
                "category": "tutorials"
            },
            {
                "path": "C:/kb/file2.md",
                "name": "file2.md",
                "agent": "character-pipeline",
                "size": 1024,
                "modified": "2025-11-07T09:00:00",
                "category": "ip-adapter-knowledge"
            }
        ]

        with patch('api.knowledge.scan_kb_files', return_value=mock_files):
            response = test_client.get("/api/knowledge/files")

            assert response.status_code == 200
            data = response.json()

            assert "files" in data
            assert "meta" in data

    def test_get_kb_files_filtered_by_agent(self, test_client):
        """Test filtering knowledge base files by agent"""
        mock_files = [
            {"path": "test.md", "name": "test.md", "agent": "character-pipeline", "size": 1024, "modified": "2025-11-07T09:00:00", "category": "workflows"}
        ]

        with patch('api.knowledge.scan_kb_files', return_value=mock_files):
            response = test_client.get("/api/knowledge/files?agent=character-pipeline")

            assert response.status_code == 200
            data = response.json()

            assert "files" in data

    def test_get_creators_list(self, test_client):
        """Test listing YouTube creators"""
        mock_creator_db = {
            "metadata": {"total_creators": 38},
            "creators": [
                {
                    "id": "instasd",
                    "name": "InstaSD",
                    "priority": "critical",
                    "focus": "ComfyUI workflows"
                },
                {
                    "id": "automation-avenue",
                    "name": "Automation Avenue",
                    "priority": "critical",
                    "focus": "Automation"
                }
            ],
            "priority_tiers": {"critical": 5, "high": 10}
        }

        with patch('api.knowledge.load_creator_database', return_value=mock_creator_db):
            response = test_client.get("/api/knowledge/creators")

            assert response.status_code == 200
            data = response.json()

            assert "total" in data
            assert "creators" in data
            assert len(data["creators"]) == 2

    def test_get_creators_filtered_by_priority(self, test_client):
        """Test filtering creators by priority"""
        mock_creator_db = {
            "creators": [
                {"id": "instasd", "name": "InstaSD", "priority": "critical"},
                {"id": "low-priority", "name": "Low Priority", "priority": "low"}
            ],
            "priority_tiers": {}
        }

        with patch('api.knowledge.load_creator_database', return_value=mock_creator_db):
            response = test_client.get("/api/knowledge/creators?priority=critical")

            assert response.status_code == 200
            data = response.json()

            # Should filter to only critical priority
            assert all(c.get("priority") == "critical" for c in data.get("creators", []))

    def test_get_creator_details(self, test_client):
        """Test getting specific creator details"""
        mock_creator_db = {
            "creators": [
                {
                    "id": "instasd",
                    "name": "InstaSD",
                    "priority": "critical",
                    "focus": "ComfyUI workflows"
                }
            ]
        }
        mock_files = []

        with patch('api.knowledge.load_creator_database', return_value=mock_creator_db), \
             patch('api.knowledge.scan_kb_files', return_value=mock_files):
            response = test_client.get("/api/knowledge/creators/instasd")

            assert response.status_code == 200
            data = response.json()

            assert data["id"] == "instasd"
            assert data["name"] == "InstaSD"

    def test_creator_not_found(self, test_client):
        """Test accessing non-existent creator"""
        mock_creator_db = {
            "creators": []
        }

        with patch('api.knowledge.load_creator_database', return_value=mock_creator_db):
            response = test_client.get("/api/knowledge/creators/nonexistent")

            assert response.status_code == 404

    def test_search_knowledge_base(self, test_client):
        """Test searching knowledge base content"""
        mock_files = [
            {
                "path": "C:/kb/test.md",
                "name": "test.md",
                "agent": "character-pipeline",
                "size": 1024,
                "modified": "2025-11-07T09:00:00",
                "category": "workflows"
            }
        ]

        with patch('api.knowledge.scan_kb_files', return_value=mock_files), \
             patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "IP-Adapter content here"
            response = test_client.get("/api/knowledge/search?query=IP-Adapter")

            assert response.status_code == 200
            data = response.json()

            assert "query" in data
            assert "results" in data

    def test_search_empty_query(self, test_client):
        """Test search with too short query"""
        response = test_client.get("/api/knowledge/search?query=a")

        # Query must be at least 2 characters
        assert response.status_code == 422  # Validation error

    def test_cache_invalidation(self, test_client):
        """Test cache invalidation endpoint"""
        with patch('api.knowledge.load_creator_database') as mock_creator, \
             patch('api.knowledge.scan_kb_files') as mock_scan, \
             patch('api.knowledge.kb_cache') as mock_cache:
            # Setup mock invalidate methods
            mock_creator.invalidate = Mock()
            mock_scan.invalidate = Mock()
            mock_cache.clear = Mock()

            response = test_client.post("/api/knowledge/cache/invalidate")

            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "success"

    def test_cache_stats(self, test_client):
        """Test cache statistics endpoint"""
        mock_cache_stats = {"hits": 10, "misses": 5, "size": 3}

        with patch('api.knowledge.load_creator_database') as mock_creator, \
             patch('api.knowledge.scan_kb_files') as mock_scan, \
             patch('api.knowledge.kb_cache') as mock_cache:
            # Setup mock cache with get_stats method
            mock_creator.cache = Mock()
            mock_creator.cache.get_stats = Mock(return_value=mock_cache_stats)
            mock_scan.cache = Mock()
            mock_scan.cache.get_stats = Mock(return_value=mock_cache_stats)
            mock_cache.get_stats = Mock(return_value=mock_cache_stats)

            response = test_client.get("/api/knowledge/cache/stats")

            assert response.status_code == 200

    def test_get_scan_jobs(self, test_client):
        """Test getting scan job history"""
        with patch('pathlib.Path.exists', return_value=False):
            response = test_client.get("/api/knowledge/jobs")

            assert response.status_code == 200
            data = response.json()

            assert "total" in data
            assert "jobs" in data

    def test_trigger_manual_scan(self, test_client):
        """Test triggering manual KB scan"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('subprocess.Popen') as mock_popen:
            mock_popen.return_value.pid = 12345

            response = test_client.post("/api/knowledge/scan?creator_id=instasd")

            assert response.status_code == 200
            data = response.json()

            assert data.get("status") == "started"
            assert "pid" in data
