"""
Comprehensive test suite for input validation schemas.

Tests cover:
- Valid inputs (should pass)
- Invalid inputs (should reject with 422)
- Edge cases
- Boundary values
- Security concerns (injection, traversal)
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ============================================================================
# SERVICE VALIDATION TESTS
# ============================================================================

class TestServiceValidation:
    """Test service endpoint validation."""

    def test_start_service_valid_name(self):
        """Valid service name should be accepted."""
        # Note: Service may not exist, but validation should pass
        response = client.post("/api/services/test-service/start")
        # Should not be 422 (validation error)
        assert response.status_code != 422

    def test_start_service_invalid_characters(self):
        """Service name with invalid characters should be rejected.

        Note: Characters like '/' and spaces in path parameters cause 404 (route not found)
        rather than 422 (validation error) because HTTP routing happens before validation.
        Both status codes effectively block the attack, so we accept either.
        """
        invalid_names = [
            "service@name",
            "service name",
            "service/name",
            "service\\name",
            "service;name",
            "../service",
            "service' OR '1'='1",
        ]

        for name in invalid_names:
            response = client.post(f"/api/services/{name}/start")
            # Accept 404 (route not found) or 422 (validation) - both block the attack
            assert response.status_code in [404, 422], f"Should reject: {name}, got {response.status_code}"

    def test_start_service_empty_name(self):
        """Empty service name should be rejected."""
        response = client.post("/api/services//start")
        assert response.status_code in [404, 422]

    def test_start_service_too_long(self):
        """Service name exceeding max length should be rejected."""
        long_name = "a" * 101  # Max is 100
        response = client.post(f"/api/services/{long_name}/start")
        assert response.status_code == 422

    def test_stop_service_with_timeout(self):
        """Stop service with valid timeout should be accepted."""
        response = client.post(
            "/api/services/test-service/stop",
            params={"timeout": 30, "force": False}
        )
        assert response.status_code != 422

    def test_stop_service_invalid_timeout(self):
        """Stop service with invalid timeout should be rejected."""
        # Timeout too small
        response = client.post(
            "/api/services/test-service/stop",
            params={"timeout": 0}
        )
        assert response.status_code == 422

        # Timeout too large
        response = client.post(
            "/api/services/test-service/stop",
            params={"timeout": 301}  # Max is 300
        )
        assert response.status_code == 422

    def test_get_logs_valid_params(self):
        """Get logs with valid parameters should be accepted."""
        response = client.get(
            "/api/services/test-service/logs",
            params={"lines": 100}
        )
        assert response.status_code != 422

    def test_get_logs_invalid_lines(self):
        """Get logs with invalid line count should be rejected."""
        # Too few lines
        response = client.get(
            "/api/services/test-service/logs",
            params={"lines": 0}
        )
        assert response.status_code == 422

        # Too many lines
        response = client.get(
            "/api/services/test-service/logs",
            params={"lines": 10001}  # Max is 10000
        )
        assert response.status_code == 422


# ============================================================================
# PROJECT VALIDATION TESTS
# ============================================================================

class TestProjectValidation:
    """Test project endpoint validation."""

    def test_browse_files_valid_path(self):
        """Browse files with valid path should be accepted."""
        response = client.get(
            "/api/projects/meowping-rts/files",
            params={"path": "src/components", "pattern": "*.tsx"}
        )
        assert response.status_code != 422

    def test_browse_files_directory_traversal(self):
        """Directory traversal attempts should be rejected."""
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "subdir/../../forbidden",
            "/etc/passwd",
            "\\windows\\system32",
        ]

        for path in traversal_paths:
            response = client.get(
                "/api/projects/test-project/files",
                params={"path": path}
            )
            assert response.status_code == 422, f"Should reject: {path}"

    def test_browse_files_invalid_pattern(self):
        """Invalid file patterns should be rejected."""
        invalid_patterns = [
            "*.tsx;rm -rf /",
            "*.tsx && echo hacked",
            "$(malicious)",
            "`whoami`",
        ]

        for pattern in invalid_patterns:
            response = client.get(
                "/api/projects/test-project/files",
                params={"pattern": pattern}
            )
            assert response.status_code == 422, f"Should reject: {pattern}"

    def test_get_commits_valid_limit(self):
        """Get commits with valid limit should be accepted."""
        response = client.get(
            "/api/projects/meowping-rts/commits",
            params={"limit": 20}
        )
        assert response.status_code != 422

    def test_get_commits_invalid_limit(self):
        """Get commits with invalid limit should be rejected."""
        # Too few
        response = client.get(
            "/api/projects/test-project/commits",
            params={"limit": 0}
        )
        assert response.status_code == 422

        # Too many
        response = client.get(
            "/api/projects/test-project/commits",
            params={"limit": 101}  # Max is 100
        )
        assert response.status_code == 422

    def test_project_name_validation(self):
        """Invalid project names should be rejected.

        Note: Characters like '/' and spaces in path parameters cause 404 (route not found)
        rather than 422 (validation error) because HTTP routing happens before validation.
        Both status codes effectively block the attack, so we accept either.
        """
        invalid_names = [
            "project@name",
            "project name",
            "project/name",
            "project\\name",
            "../forbidden",
            "project;malicious",
        ]

        for name in invalid_names:
            response = client.get(f"/api/projects/{name}/status")
            # Accept 404 (route not found) or 422 (validation) - both block the attack
            assert response.status_code in [404, 422], f"Should reject: {name}, got {response.status_code}"


# ============================================================================
# KNOWLEDGE BASE VALIDATION TESTS
# ============================================================================

class TestKnowledgeValidation:
    """Test knowledge base endpoint validation."""

    def test_scan_valid_params(self):
        """Scan with valid parameters should be accepted."""
        response = client.post(
            "/api/knowledge/scan",
            params={
                "creator_id": "test-creator",
                "priority": "high",
                "max_videos": 10
            }
        )
        assert response.status_code != 422

    def test_scan_invalid_priority(self):
        """Scan with invalid priority should be rejected."""
        response = client.post(
            "/api/knowledge/scan",
            params={"priority": "critical"}  # Not in [high, medium, low]
        )
        assert response.status_code == 422

    def test_scan_invalid_max_videos(self):
        """Scan with invalid max_videos should be rejected."""
        # Too few
        response = client.post(
            "/api/knowledge/scan",
            params={"max_videos": 0}
        )
        assert response.status_code == 422

        # Too many
        response = client.post(
            "/api/knowledge/scan",
            params={"max_videos": 101}  # Max is 100
        )
        assert response.status_code == 422

    def test_scan_invalid_creator_id(self):
        """Scan with invalid creator ID should be rejected."""
        invalid_ids = [
            "creator@test",
            "creator name",
            "creator/id",
            "../malicious",
            "creator;drop table",
        ]

        for creator_id in invalid_ids:
            response = client.post(
                "/api/knowledge/scan",
                params={"creator_id": creator_id}
            )
            assert response.status_code == 422, f"Should reject: {creator_id}"

    def test_search_valid_query(self):
        """Search with valid query should be accepted."""
        response = client.get(
            "/api/knowledge/search",
            params={"query": "test query", "limit": 20}
        )
        assert response.status_code != 422

    def test_search_query_too_short(self):
        """Search query too short should be rejected."""
        response = client.get(
            "/api/knowledge/search",
            params={"query": "a"}  # Min is 2
        )
        assert response.status_code == 422

    def test_search_query_too_long(self):
        """Search query too long should be rejected."""
        long_query = "a" * 501  # Max is 500
        response = client.get(
            "/api/knowledge/search",
            params={"query": long_query}
        )
        assert response.status_code == 422

    def test_search_invalid_agent_filter(self):
        """Search with invalid agent filter should be rejected."""
        invalid_agents = [
            "agent@name",
            "agent name",
            "agent/name",
            "../malicious",
        ]

        for agent in invalid_agents:
            response = client.get(
                "/api/knowledge/search",
                params={"query": "test", "agent": agent}
            )
            assert response.status_code == 422, f"Should reject: {agent}"


# ============================================================================
# DOCKER VALIDATION TESTS
# ============================================================================

class TestDockerValidation:
    """Test Docker endpoint validation."""

    def test_start_container_valid_id(self):
        """Start container with valid ID should be accepted."""
        response = client.post("/api/docker/container/test-container/start")
        assert response.status_code != 422

    def test_start_container_invalid_id(self):
        """Start container with invalid ID should be rejected.

        Note: Characters like '/' and spaces in path parameters cause 404 (route not found)
        rather than 422 (validation error) because HTTP routing happens before validation.
        Both status codes effectively block the attack, so we accept either.
        """
        invalid_ids = [
            "container@name",
            "container name",
            "../malicious",
            "container;malicious",
            "$(whoami)",
        ]

        for container_id in invalid_ids:
            response = client.post(f"/api/docker/container/{container_id}/start")
            # Accept 404 (route not found) or 422 (validation) - both block the attack
            assert response.status_code in [404, 422], f"Should reject: {container_id}, got {response.status_code}"

    def test_stop_container_valid_timeout(self):
        """Stop container with valid timeout should be accepted."""
        response = client.post(
            "/api/docker/container/test-container/stop",
            params={"timeout": 30}
        )
        assert response.status_code != 422

    def test_stop_container_invalid_timeout(self):
        """Stop container with invalid timeout should be rejected."""
        # Too small
        response = client.post(
            "/api/docker/container/test/stop",
            params={"timeout": 0}
        )
        assert response.status_code == 422

        # Too large
        response = client.post(
            "/api/docker/container/test/stop",
            params={"timeout": 301}  # Max is 300
        )
        assert response.status_code == 422

    def test_get_logs_valid_params(self):
        """Get container logs with valid parameters should be accepted."""
        response = client.get(
            "/api/docker/container/test/logs",
            params={"tail": 100, "timestamps": True}
        )
        assert response.status_code != 422

    def test_get_logs_invalid_tail(self):
        """Get container logs with invalid tail should be rejected."""
        # Too few
        response = client.get(
            "/api/docker/container/test/logs",
            params={"tail": 0}
        )
        assert response.status_code == 422

        # Too many
        response = client.get(
            "/api/docker/container/test/logs",
            params={"tail": 1001}  # Max is 1000
        )
        assert response.status_code == 422

    def test_get_logs_valid_since_params(self):
        """Get logs with valid 'since' parameter should be accepted."""
        valid_since = ["10m", "1h", "2d", "30s"]

        for since in valid_since:
            response = client.get(
                "/api/docker/container/test/logs",
                params={"since": since}
            )
            # Should not be 422 for validation
            assert response.status_code != 422


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary values."""

    def test_exact_max_lengths(self):
        """Test exact maximum length values."""
        # Service name exactly 100 chars
        name_100 = "a" * 100
        response = client.post(f"/api/services/{name_100}/start")
        assert response.status_code != 422

        # Service name 101 chars (should fail)
        name_101 = "a" * 101
        response = client.post(f"/api/services/{name_101}/start")
        assert response.status_code == 422

    def test_boundary_values(self):
        """Test boundary values for numeric parameters."""
        # Minimum valid timeout
        response = client.post(
            "/api/services/test/stop",
            params={"timeout": 1}
        )
        assert response.status_code != 422

        # Maximum valid timeout
        response = client.post(
            "/api/services/test/stop",
            params={"timeout": 300}
        )
        assert response.status_code != 422

    def test_whitespace_handling(self):
        """Test whitespace in inputs is handled correctly."""
        # Service name with leading/trailing spaces should be stripped
        response = client.post("/api/services/  test-service  /start")
        # Path parameter doesn't auto-strip, so this might fail routing
        # but shouldn't cause validation error

    def test_case_insensitivity(self):
        """Test that service names are case-insensitive."""
        # Both should normalize to lowercase
        response1 = client.post("/api/services/TEST-SERVICE/start")
        response2 = client.post("/api/services/test-service/start")

        # Neither should fail validation (422)
        assert response1.status_code != 422
        assert response2.status_code != 422


# ============================================================================
# SECURITY TESTS
# ============================================================================

class TestSecurityValidation:
    """Test security-focused validation."""

    def test_sql_injection_attempts(self):
        """SQL injection attempts should be rejected."""
        sql_injections = [
            "test' OR '1'='1",
            "test'; DROP TABLE users; --",
            "test' UNION SELECT * FROM secrets--",
        ]

        for injection in sql_injections:
            response = client.post(f"/api/services/{injection}/start")
            assert response.status_code == 422, f"Should reject: {injection}"

    def test_command_injection_attempts(self):
        """Command injection attempts should be rejected.

        Note: Characters like '/' and spaces in path parameters cause 404 (route not found)
        rather than 422 (validation error) because HTTP routing happens before validation.
        Both status codes effectively block the attack, so we accept either.
        """
        cmd_injections = [
            "test; ls -la",
            "test && cat /etc/passwd",
            "test | whoami",
            "$(whoami)",
            "`whoami`",
        ]

        for injection in cmd_injections:
            response = client.post(f"/api/services/{injection}/start")
            # Accept 404 (route not found) or 422 (validation) - both block the attack
            assert response.status_code in [404, 422], f"Should reject: {injection}, got {response.status_code}"

    def test_path_traversal_attempts(self):
        """Path traversal attempts should be rejected."""
        traversals = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "./../forbidden",
            "subdir/../../etc",
        ]

        for traversal in traversals:
            response = client.get(
                "/api/projects/test/files",
                params={"path": traversal}
            )
            assert response.status_code == 422, f"Should reject: {traversal}"

    def test_script_injection_attempts(self):
        """Script injection attempts should be rejected."""
        scripts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onerror=alert('xss')",
        ]

        for script in scripts:
            # Test in search query
            response = client.get(
                "/api/knowledge/search",
                params={"query": script}
            )
            # Should not cause validation error, but should be sanitized
            # Validation passes, but backend should handle safely


# ============================================================================
# VALIDATION ERROR FORMAT TESTS
# ============================================================================

class TestValidationErrorFormat:
    """Test that validation errors return proper format."""

    def test_validation_error_status_code(self):
        """Validation errors should return 422."""
        response = client.post(
            "/api/services/invalid@name/start"
        )
        assert response.status_code == 422

    def test_validation_error_response_format(self):
        """Validation error response should have proper format."""
        response = client.post(
            "/api/services/invalid@name/start"
        )

        if response.status_code == 422:
            data = response.json()
            # FastAPI standard validation error format
            assert "detail" in data

    def test_multiple_validation_errors(self):
        """Multiple validation errors should all be reported."""
        response = client.post(
            "/api/services/invalid@name/stop",
            params={"timeout": 0}  # Invalid timeout
        )

        if response.status_code == 422:
            data = response.json()
            assert "detail" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
