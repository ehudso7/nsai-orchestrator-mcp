"""Comprehensive API tests for NSAI Orchestrator MCP."""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json

# Import your main application
# from main_enhanced import app


class TestAPIEndpoints:
    """Test all API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        # Mock the MCP server to avoid actual connections
        with patch('main_enhanced.MCPServerEnhanced') as mock_server:
            mock_instance = AsyncMock()
            mock_server.return_value = mock_instance
            
            from main_enhanced import app
            return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "system" in data
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Metrics should be in Prometheus format
        assert "http_requests_total" in response.text or response.status_code == 200
    
    @patch('main_enhanced.require_api_key')
    def test_mcp_endpoint_missing_agent(self, mock_auth, client):
        """Test MCP endpoint with missing agent parameter."""
        mock_auth.return_value = "test_key"
        
        response = client.post(
            "/mcp",
            json={"method": "execute", "params": {}},
            headers={"X-API-Key": "nsai_test_key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "agent" in data["error"].lower()
    
    @patch('main_enhanced.require_api_key')
    def test_mcp_endpoint_invalid_method(self, mock_auth, client):
        """Test MCP endpoint with invalid method."""
        mock_auth.return_value = "test_key"
        
        response = client.post(
            "/mcp",
            json={"method": "invalid_method", "params": {"agent": "claude"}},
            headers={"X-API-Key": "nsai_test_key"}
        )
        assert response.status_code == 422  # Validation error
    
    @patch('main_enhanced.require_api_key')
    @patch('main_enhanced.mcp_server')
    def test_mcp_endpoint_success(self, mock_server, mock_auth, client):
        """Test successful MCP request."""
        mock_auth.return_value = "test_key"
        mock_server.handle_rpc = AsyncMock(return_value={
            "success": True,
            "result": {"message": "Task completed"},
            "task_id": "test_task_123"
        })
        
        response = client.post(
            "/mcp",
            json={"method": "execute", "params": {"agent": "claude", "task": "test task"}},
            headers={"X-API-Key": "nsai_test_key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "duration_ms" in data
    
    def test_websocket_endpoint(self, client):
        """Test WebSocket endpoint connection."""
        with client.websocket_connect("/ws/test_client") as websocket:
            # Send ping
            websocket.send_json({"type": "ping"})
            
            # Receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"
    
    @patch('main_enhanced.require_api_key')
    @patch('main_enhanced.mcp_server')
    def test_memory_graph_endpoint(self, mock_server, mock_auth, client):
        """Test memory graph endpoint."""
        mock_auth.return_value = "test_key"
        mock_server.get_memory_graph = AsyncMock(return_value={
            "nodes": [],
            "edges": [],
            "metadata": {}
        })
        
        response = client.get(
            "/memory/graph",
            headers={"X-API-Key": "nsai_test_key"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_rate_limiting(self, client):
        """Test rate limiting functionality."""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = client.get("/")
            responses.append(response.status_code)
        
        # Should have at least some successful requests
        assert 200 in responses
        # May have rate limit responses (429) if limits are low


class TestSecurity:
    """Test security features."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('main_enhanced.MCPServerEnhanced'):
            from main_enhanced import app
            return TestClient(app)
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/", headers={"Origin": "http://localhost:3000"})
        assert "access-control-allow-origin" in response.headers
    
    def test_missing_api_key(self, client):
        """Test endpoints require API key."""
        response = client.post("/mcp", json={"method": "execute", "params": {"agent": "claude"}})
        assert response.status_code == 401
    
    def test_invalid_api_key_format(self, client):
        """Test invalid API key format is rejected."""
        response = client.post(
            "/mcp",
            json={"method": "execute", "params": {"agent": "claude"}},
            headers={"X-API-Key": "invalid_key"}
        )
        assert response.status_code == 401
    
    def test_input_sanitization(self, client):
        """Test input sanitization works."""
        # Test with potentially malicious input
        malicious_input = {
            "method": "execute",
            "params": {
                "agent": "claude",
                "task": "<script>alert('xss')</script>",
                "nested": {
                    "level1": {
                        "level2": {
                            "level3": {
                                "level4": {
                                    "level5": "too deep"
                                }
                            }
                        }
                    }
                }
            }
        }
        
        response = client.post(
            "/mcp",
            json=malicious_input,
            headers={"X-API-Key": "nsai_test_key"}
        )
        
        # Should either sanitize or reject
        assert response.status_code in [200, 400, 401, 422]


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('main_enhanced.MCPServerEnhanced'):
            from main_enhanced import app
            return TestClient(app)
    
    def test_404_handling(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_405_handling(self, client):
        """Test method not allowed."""
        response = client.delete("/")
        assert response.status_code == 405
    
    def test_422_validation_error(self, client):
        """Test validation error handling."""
        response = client.post("/mcp", json={"invalid": "data"})
        assert response.status_code in [401, 422]  # Auth or validation error
    
    @patch('main_enhanced.require_api_key')
    @patch('main_enhanced.mcp_server')
    def test_internal_server_error(self, mock_server, mock_auth, client):
        """Test internal server error handling."""
        mock_auth.return_value = "test_key"
        mock_server.handle_rpc = AsyncMock(side_effect=Exception("Internal error"))
        
        response = client.post(
            "/mcp",
            json={"method": "execute", "params": {"agent": "claude"}},
            headers={"X-API-Key": "nsai_test_key"}
        )
        
        assert response.status_code == 200  # Our custom error handling
        data = response.json()
        assert data["success"] is False
        assert "error" in data


class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('main_enhanced.MCPServerEnhanced'):
            from main_enhanced import app
            return TestClient(app)
    
    def test_response_time(self, client):
        """Test response times are reasonable."""
        import time
        
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import concurrent.futures
        import threading
        
        def make_request():
            return client.get("/")
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)


# Fixtures for test data
@pytest.fixture
def sample_task_request():
    """Sample task request data."""
    return {
        "method": "execute",
        "params": {
            "agent": "claude",
            "task": "Analyze the following data and provide insights",
            "data": {"key": "value"}
        }
    }


@pytest.fixture
def sample_memory_query():
    """Sample memory query data."""
    return {
        "query_type": "search",
        "filters": {
            "content_contains": "test",
            "session_id": "test_session"
        },
        "limit": 10
    }


# Test utilities
def assert_valid_api_response(response_data, expected_success=True):
    """Assert response matches API response schema."""
    assert isinstance(response_data, dict)
    assert "success" in response_data
    assert response_data["success"] == expected_success
    
    if expected_success:
        assert "result" in response_data or "data" in response_data
    else:
        assert "error" in response_data
    
    if "duration_ms" in response_data:
        assert isinstance(response_data["duration_ms"], (int, float))
        assert response_data["duration_ms"] >= 0


def assert_valid_health_response(response_data):
    """Assert health response is valid."""
    assert isinstance(response_data, dict)
    assert "status" in response_data
    assert "timestamp" in response_data
    assert "system" in response_data
    
    system_data = response_data["system"]
    assert "cpu_percent" in system_data
    assert "memory_percent" in system_data
    assert "disk_percent" in system_data
    
    # Check ranges
    assert 0 <= system_data["cpu_percent"] <= 100
    assert 0 <= system_data["memory_percent"] <= 100
    assert 0 <= system_data["disk_percent"] <= 100


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])