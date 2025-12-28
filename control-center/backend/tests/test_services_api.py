"""
Tests for Service Control API endpoints

Mock paths corrected by ARGUS QA Lead - 2025-12-28
Original mock paths (services.service_controller.*) were non-existent.
Actual implementation uses services.service_manager.ServiceManager class.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestServicesAPI:
    """Test service control endpoints"""

    def test_list_services(self, test_client):
        """Test listing all services"""
        mock_services = [
            {"name": "comfyui", "status": "running", "pid": 12345, "port": 8188},
            {"name": "knowledge-base", "status": "stopped", "pid": None, "port": 5000}
        ]

        with patch('services.service_manager.ServiceManager.get_all_services', new_callable=AsyncMock, return_value=mock_services):
            response = test_client.get("/api/services")

            assert response.status_code == 200
            data = response.json()

            assert "services" in data
            assert data["success"] is True

    def test_get_service_status(self, test_client):
        """Test getting individual service status"""
        mock_status = {
            "name": "comfyui",
            "status": "running",
            "pid": 12345,
            "port": 8188,
            "uptime": 3600,
            "cpu": 8.5,
            "memory": 512
        }

        with patch('services.service_manager.ServiceManager.get_service_status', new_callable=AsyncMock, return_value=mock_status):
            response = test_client.get("/api/services/comfyui/status")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["status"] == "running"
            assert data["pid"] == 12345

    def test_start_service_success(self, test_client):
        """Test starting a service successfully"""
        mock_result = {
            "success": True,
            "message": "ComfyUI started successfully",
            "pid": 12345,
            "port": 8188
        }

        with patch('services.service_manager.ServiceManager.start_service', new_callable=AsyncMock, return_value=mock_result):
            response = test_client.post("/api/services/comfyui/start")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["pid"] == 12345

    def test_stop_service_success(self, test_client):
        """Test stopping a running service"""
        mock_result = {
            "success": True,
            "message": "ComfyUI stopped successfully"
        }

        with patch('services.service_manager.ServiceManager.stop_service', new_callable=AsyncMock, return_value=mock_result):
            response = test_client.post("/api/services/comfyui/stop")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True

    def test_restart_service(self, test_client):
        """Test restarting a service"""
        mock_result = {
            "success": True,
            "message": "ComfyUI restarted successfully",
            "pid": 12346  # New PID after restart
        }

        with patch('services.service_manager.ServiceManager.restart_service', new_callable=AsyncMock, return_value=mock_result):
            response = test_client.post("/api/services/comfyui/restart")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["pid"] == 12346

    def test_get_service_logs(self, test_client):
        """Test retrieving service logs"""
        mock_logs = {
            "logs": [
                {"timestamp": "2025-11-07T12:00:00", "level": "INFO", "message": "Server started"},
                {"timestamp": "2025-11-07T12:01:00", "level": "INFO", "message": "Processing request"}
            ],
            "count": 2
        }

        with patch('services.service_manager.ServiceManager.get_service_logs', new_callable=AsyncMock, return_value=mock_logs):
            response = test_client.get("/api/services/comfyui/logs")

            assert response.status_code == 200
            data = response.json()

            assert "logs" in data
            assert len(data["logs"]) == 2

    def test_service_not_found(self, test_client):
        """Test accessing non-existent service"""
        with patch('services.service_manager.ServiceManager.get_service_status', new_callable=AsyncMock, side_effect=Exception("Service not found")):
            response = test_client.get("/api/services/nonexistent/status")

            # Should return error (500 or 404 depending on implementation)
            assert response.status_code in [404, 500]

    def test_start_service_error(self, test_client):
        """Test error handling during service start"""
        with patch('services.service_manager.ServiceManager.start_service', new_callable=AsyncMock, side_effect=Exception("Start failed")):
            response = test_client.post("/api/services/comfyui/start")

            assert response.status_code == 500

    def test_invalid_service_name_characters(self, test_client):
        """Test service names with invalid characters"""
        # Service name pattern: ^[a-zA-Z0-9_-]+$
        response = test_client.get("/api/services/invalid@service!/status")

        # Should fail validation
        assert response.status_code == 422

    def test_service_stop_with_timeout(self, test_client):
        """Test stopping a service with custom timeout"""
        mock_result = {
            "success": True,
            "message": "ComfyUI stopped successfully"
        }

        with patch('services.service_manager.ServiceManager.stop_service', new_callable=AsyncMock, return_value=mock_result):
            response = test_client.post("/api/services/comfyui/stop?timeout=30")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_get_service_logs_with_line_limit(self, test_client):
        """Test getting service logs with custom line limit"""
        mock_logs = {
            "logs": [{"timestamp": "2025-11-07T12:00:00", "level": "INFO", "message": "Log line"}],
            "count": 1
        }

        with patch('services.service_manager.ServiceManager.get_service_logs', new_callable=AsyncMock, return_value=mock_logs):
            response = test_client.get("/api/services/comfyui/logs?lines=50")

            assert response.status_code == 200
            data = response.json()
            assert "logs" in data

    def test_list_services_pagination(self, test_client):
        """Test service listing with pagination"""
        mock_services = [
            {"name": f"service-{i}", "status": "running"} for i in range(100)
        ]

        with patch('services.service_manager.ServiceManager.get_all_services', new_callable=AsyncMock, return_value=mock_services):
            response = test_client.get("/api/services?page=1&page_size=10")

            assert response.status_code == 200
            data = response.json()

            assert "services" in data
            assert "meta" in data
            assert data["meta"]["page_size"] <= 10
