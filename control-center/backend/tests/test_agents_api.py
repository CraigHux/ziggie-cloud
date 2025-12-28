"""
Tests for AI Agents API endpoints

Mock paths corrected by ARGUS QA Lead - 2025-12-28
Original mock paths (services.agent_manager.*) were non-existent.
Actual implementation uses inline functions in api.agents module.
"""
import pytest
from unittest.mock import Mock, patch


class TestAgentsAPI:
    """Test AI agents management endpoints"""

    def test_list_all_agents(self, test_client, mock_agent_data):
        """Test listing all AI agents"""
        # Mock the actual functions used in api/agents.py
        mock_l1 = [{"id": "01_art_director", "level": "L1", "name": "Art Director"}]
        mock_l2 = [{"id": "L2.1.1", "level": "L2", "name": "Sub Agent 1"}]
        mock_l3 = [{"id": "L3.1.1.1", "level": "L3", "name": "Micro Agent 1"}]

        with patch('api.agents.load_l1_agents', return_value=mock_l1), \
             patch('api.agents.load_l2_agents', return_value=mock_l2), \
             patch('api.agents.load_l3_agents', return_value=mock_l3):
            response = test_client.get("/api/agents")

            assert response.status_code == 200
            data = response.json()

            assert "total" in data
            assert "agents" in data
            assert data["total"] == 3

    def test_get_agent_details(self, test_client):
        """Test getting specific agent details"""
        mock_l1 = [{
            "id": "01_art_director",
            "name": "Art Director",
            "level": "L1",
            "responsibilities": ["Visual style", "Asset standards"],
        }]
        mock_l2 = []
        mock_l3 = []

        with patch('api.agents.load_l1_agents', return_value=mock_l1), \
             patch('api.agents.load_l2_agents', return_value=mock_l2), \
             patch('api.agents.load_l3_agents', return_value=mock_l3):
            response = test_client.get("/api/agents/01_art_director")

            assert response.status_code == 200
            data = response.json()

            assert data["id"] == "01_art_director"
            assert data["name"] == "Art Director"

    def test_list_agents_by_level(self, test_client):
        """Test filtering agents by level"""
        mock_l1 = [
            {"id": "01_art_director", "level": "L1", "name": "Art Director"},
            {"id": "02_character_pipeline", "level": "L1", "name": "Character Pipeline"},
            {"id": "03_environment_pipeline", "level": "L1", "name": "Environment Pipeline"}
        ]
        mock_l2 = [{"id": "L2.1.1", "level": "L2", "name": "Sub Agent 1"}]
        mock_l3 = [{"id": "L3.1.1.1", "level": "L3", "name": "Micro Agent 1"}]

        with patch('api.agents.load_l1_agents', return_value=mock_l1), \
             patch('api.agents.load_l2_agents', return_value=mock_l2), \
             patch('api.agents.load_l3_agents', return_value=mock_l3):
            response = test_client.get("/api/agents?level=L1")

            assert response.status_code == 200
            data = response.json()

            # Verify only L1 agents returned
            assert all(agent.get("level") == "L1" for agent in data.get("agents", []))

    def test_get_agent_knowledge_access(self, test_client):
        """Test getting agent's knowledge base access"""
        # The /api/agents/{agent_id}/knowledge endpoint exists in api/agents.py
        # It returns files from the knowledge base directory
        mock_l1 = [{"id": "01_art_director", "level": "L1", "name": "Art Director"}]

        with patch('api.agents.load_l1_agents', return_value=mock_l1), \
             patch('api.agents.load_l2_agents', return_value=[]), \
             patch('api.agents.load_l3_agents', return_value=[]), \
             patch('os.path.exists', return_value=False):
            response = test_client.get("/api/agents/01_art_director/knowledge")

            assert response.status_code == 200
            data = response.json()

            assert "agent_id" in data
            assert "files" in data

    def test_get_agent_stats(self, test_client):
        """Test getting agent statistics"""
        mock_l1 = [
            {"id": "01_art_director", "level": "L1", "name": "Art Director", "title": "Art Director"}
        ]
        mock_l2 = [{"id": "L2.1.1", "level": "L2", "parent_l1": "01"}]
        mock_l3 = [{"id": "L3.1.1.1", "level": "L3", "parent_l1": "01"}]

        with patch('api.agents.load_l1_agents', return_value=mock_l1), \
             patch('api.agents.load_l2_agents', return_value=mock_l2), \
             patch('api.agents.load_l3_agents', return_value=mock_l3):
            response = test_client.get("/api/agents/stats")

            assert response.status_code == 200
            data = response.json()

            assert "total" in data
            assert "by_level" in data
            assert data["total"] == 3

    def test_get_agent_hierarchy(self, test_client):
        """Test getting agent hierarchy structure"""
        mock_l1 = [{"id": "01_art_director", "level": "L1", "name": "Art Director"}]
        mock_l2 = [{"id": "L2.1.1", "level": "L2", "parent_l1": "01", "name": "Sub Agent 1"}]
        mock_l3 = [{"id": "L3.1.1.1", "level": "L3", "parent_l1": "01", "parent_l2": "L2.1.1", "name": "Micro Agent 1"}]

        with patch('api.agents.load_l1_agents', return_value=mock_l1), \
             patch('api.agents.load_l2_agents', return_value=mock_l2), \
             patch('api.agents.load_l3_agents', return_value=mock_l3):
            response = test_client.get("/api/agents/01_art_director/hierarchy")

            assert response.status_code == 200
            data = response.json()

            assert "agent" in data
            assert "children" in data

    def test_agent_not_found(self, test_client):
        """Test accessing non-existent agent"""
        with patch('api.agents.load_l1_agents', return_value=[]), \
             patch('api.agents.load_l2_agents', return_value=[]), \
             patch('api.agents.load_l3_agents', return_value=[]):
            response = test_client.get("/api/agents/L99.99")

            # The API should return 404 or appropriate error
            assert response.status_code in [404, 500]

    def test_list_agents_with_search(self, test_client):
        """Test searching agents by name"""
        mock_l1 = [
            {"id": "01_art_director", "level": "L1", "name": "Art Director", "title": "Art Director", "role": "Art"},
            {"id": "02_character_pipeline", "level": "L1", "name": "Character Pipeline", "title": "Character", "role": "Character"}
        ]

        with patch('api.agents.load_l1_agents', return_value=mock_l1), \
             patch('api.agents.load_l2_agents', return_value=[]), \
             patch('api.agents.load_l3_agents', return_value=[]):
            response = test_client.get("/api/agents?search=art")

            assert response.status_code == 200
            data = response.json()

            # Should filter to agents matching "art"
            assert "agents" in data

    def test_cache_invalidation(self, test_client):
        """Test cache invalidation endpoint"""
        with patch('api.agents.load_l1_agents') as mock_l1, \
             patch('api.agents.load_l2_agents') as mock_l2, \
             patch('api.agents.load_l3_agents') as mock_l3, \
             patch('api.agents.agents_cache') as mock_cache:
            # Setup mock invalidate methods
            mock_l1.invalidate = Mock()
            mock_l2.invalidate = Mock()
            mock_l3.invalidate = Mock()
            mock_cache.clear = Mock()

            response = test_client.post("/api/agents/cache/invalidate")

            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "success"

    def test_cache_stats(self, test_client):
        """Test cache statistics endpoint"""
        mock_cache_stats = {"hits": 10, "misses": 5, "size": 3}

        with patch('api.agents.load_l1_agents') as mock_l1, \
             patch('api.agents.load_l2_agents') as mock_l2, \
             patch('api.agents.load_l3_agents') as mock_l3, \
             patch('api.agents.agents_cache') as mock_cache:
            # Setup mock cache attribute with get_stats method
            mock_l1.cache = Mock()
            mock_l1.cache.get_stats = Mock(return_value=mock_cache_stats)
            mock_l2.cache = Mock()
            mock_l2.cache.get_stats = Mock(return_value=mock_cache_stats)
            mock_l3.cache = Mock()
            mock_l3.cache.get_stats = Mock(return_value=mock_cache_stats)
            mock_cache.get_stats = Mock(return_value=mock_cache_stats)

            response = test_client.get("/api/agents/cache/stats")

            assert response.status_code == 200
