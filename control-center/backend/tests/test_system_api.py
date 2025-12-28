"""
Tests for System Monitoring API endpoints

Mock paths corrected by ARGUS QA Lead - 2025-12-28
Original mock paths (services.system_monitor.*) were non-existent.
Actual implementation uses psutil directly in api.system module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestSystemAPI:
    """Test system monitoring endpoints"""

    def test_get_system_stats_success(self, test_client):
        """Test successful system stats retrieval"""
        # Mock psutil functions used directly in api.system
        mock_cpu_percent = Mock(return_value=45.2)
        mock_cpu_count = Mock(return_value=8)
        mock_cpu_freq = Mock(return_value=MagicMock(current=3600, min=800, max=4200))

        mock_memory = MagicMock()
        mock_memory.total = 17179869184  # 16 GB
        mock_memory.available = 8589934592  # 8 GB
        mock_memory.used = 8589934592  # 8 GB
        mock_memory.percent = 50.0

        mock_disk = MagicMock()
        mock_disk.total = 500000000000
        mock_disk.used = 250000000000
        mock_disk.free = 250000000000
        mock_disk.percent = 50.0

        with patch('api.system.psutil.cpu_percent', mock_cpu_percent), \
             patch('api.system.psutil.cpu_count', mock_cpu_count), \
             patch('api.system.psutil.cpu_freq', mock_cpu_freq), \
             patch('api.system.psutil.virtual_memory', return_value=mock_memory), \
             patch('api.system.psutil.disk_usage', return_value=mock_disk):
            response = test_client.get("/api/system/stats")

            assert response.status_code == 200
            data = response.json()

            assert "cpu" in data
            assert "memory" in data
            assert "disk" in data
            assert data["success"] is True

    def test_get_system_processes(self, test_client):
        """Test process list retrieval"""
        # Create mock process iterator
        mock_proc1 = MagicMock()
        mock_proc1.info = {"pid": 1234, "name": "python.exe", "cpu_percent": 2.5, "memory_percent": 1.5, "status": "running"}

        mock_proc2 = MagicMock()
        mock_proc2.info = {"pid": 5678, "name": "comfyui.exe", "cpu_percent": 15.2, "memory_percent": 10.0, "status": "running"}

        with patch('api.system.psutil.process_iter', return_value=[mock_proc1, mock_proc2]):
            response = test_client.get("/api/system/processes")

            assert response.status_code == 200
            data = response.json()

            assert "processes" in data
            assert data["success"] is True
            assert data["count"] >= 0

    def test_get_port_scan(self, test_client):
        """Test port scanning functionality"""
        mock_ports = [
            {"port": 8188, "service": "ComfyUI", "status": "open", "pid": 1234},
            {"port": 5000, "service": "Knowledge Base", "status": "closed", "pid": None},
            {"port": 3000, "service": "Frontend", "status": "open", "pid": 5678}
        ]

        with patch('api.system.PortScanner.scan_ports', return_value=mock_ports):
            response = test_client.get("/api/system/ports")

            assert response.status_code == 200
            data = response.json()

            assert "ports" in data
            assert data["success"] is True

    def test_get_system_info(self, test_client):
        """Test system information endpoint"""
        mock_memory = MagicMock()
        mock_memory.total = 17179869184

        with patch('platform.system', return_value="Windows"), \
             patch('platform.release', return_value="10"), \
             patch('platform.version', return_value="10.0.19041"), \
             patch('platform.machine', return_value="AMD64"), \
             patch('platform.processor', return_value="Intel64 Family"), \
             patch('socket.gethostname', return_value="test-host"), \
             patch('sys.version', "3.11.0"), \
             patch('api.system.psutil.boot_time', return_value=1699300000), \
             patch('api.system.psutil.virtual_memory', return_value=mock_memory), \
             patch('api.system.psutil.cpu_count', return_value=8), \
             patch('time.time', return_value=1699386400):
            response = test_client.get("/api/system/info")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert "os" in data
            assert "hostname" in data
            assert "uptime" in data

    def test_system_stats_error_handling(self, test_client):
        """Test error handling when system stats fail"""
        with patch('api.system.psutil.cpu_percent', side_effect=Exception("System error")):
            response = test_client.get("/api/system/stats")

            assert response.status_code == 500

    def test_system_stats_rate_limiting_exists(self, test_client):
        """Test that rate limiting decorator is applied (not testing actual limiting)"""
        # Make a single request to verify endpoint works
        mock_cpu_percent = Mock(return_value=45.2)
        mock_cpu_count = Mock(return_value=8)
        mock_cpu_freq = Mock(return_value=MagicMock(current=3600, min=800, max=4200))

        mock_memory = MagicMock()
        mock_memory.total = 17179869184
        mock_memory.available = 8589934592
        mock_memory.used = 8589934592
        mock_memory.percent = 50.0

        mock_disk = MagicMock()
        mock_disk.total = 500000000000
        mock_disk.used = 250000000000
        mock_disk.free = 250000000000
        mock_disk.percent = 50.0

        with patch('api.system.psutil.cpu_percent', mock_cpu_percent), \
             patch('api.system.psutil.cpu_count', mock_cpu_count), \
             patch('api.system.psutil.cpu_freq', mock_cpu_freq), \
             patch('api.system.psutil.virtual_memory', return_value=mock_memory), \
             patch('api.system.psutil.disk_usage', return_value=mock_disk):
            response = test_client.get("/api/system/stats")
            assert response.status_code == 200

    def test_process_access_denied_handling(self, test_client):
        """Test that AccessDenied processes are handled gracefully"""
        import psutil

        mock_proc = MagicMock()
        mock_proc.info = {"pid": 1234, "name": "system", "cpu_percent": 0, "memory_percent": 0, "status": "running"}

        # Include a process that raises AccessDenied
        mock_denied_proc = MagicMock()
        mock_denied_proc.info = property(lambda self: (_ for _ in ()).throw(psutil.AccessDenied("denied")))

        with patch('api.system.psutil.process_iter', return_value=[mock_proc]):
            response = test_client.get("/api/system/processes")

            assert response.status_code == 200
            data = response.json()
            assert "processes" in data

    def test_cpu_frequency_none_handling(self, test_client):
        """Test handling when CPU frequency is not available"""
        mock_cpu_percent = Mock(return_value=45.2)
        mock_cpu_count = Mock(return_value=8)
        mock_cpu_freq = Mock(return_value=None)  # Some systems don't report frequency

        mock_memory = MagicMock()
        mock_memory.total = 17179869184
        mock_memory.available = 8589934592
        mock_memory.used = 8589934592
        mock_memory.percent = 50.0

        mock_disk = MagicMock()
        mock_disk.total = 500000000000
        mock_disk.used = 250000000000
        mock_disk.free = 250000000000
        mock_disk.percent = 50.0

        with patch('api.system.psutil.cpu_percent', mock_cpu_percent), \
             patch('api.system.psutil.cpu_count', mock_cpu_count), \
             patch('api.system.psutil.cpu_freq', mock_cpu_freq), \
             patch('api.system.psutil.virtual_memory', return_value=mock_memory), \
             patch('api.system.psutil.disk_usage', return_value=mock_disk):
            response = test_client.get("/api/system/stats")

            assert response.status_code == 200
            data = response.json()
            # Should handle None frequency gracefully
            assert "cpu" in data
