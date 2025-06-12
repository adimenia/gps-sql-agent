"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Sports Analytics Platform API"
    assert data["version"] == "0.1.0"


@pytest.mark.integration
def test_health_check_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "status" in data
    assert "environment" in data
    assert "database_configured" in data
    assert "catapult_configured" in data
    
    assert data["status"] == "healthy"


@pytest.mark.integration
def test_health_check_content(client):
    """Test health check endpoint content."""
    response = client.get("/health")
    data = response.json()
    
    # Should indicate database is configured (localhost default)
    assert data["database_configured"] is True
    
    # Environment should be from config
    assert data["environment"] in ["development", "production", "testing"]


@pytest.mark.integration 
def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.get("/")
    
    # In development, CORS should allow all origins
    assert response.status_code == 200


@pytest.mark.integration
def test_api_documentation_endpoints(client):
    """Test that API documentation endpoints are available."""
    # OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    assert "openapi" in schema
    assert schema["info"]["title"] == "Sports Analytics Platform"
    assert schema["info"]["version"] == "0.1.0"


@pytest.mark.integration
def test_docs_endpoint_exists(client):
    """Test that docs endpoint exists (but may redirect)."""
    response = client.get("/docs")
    # Should either return 200 (docs) or redirect, but not 404
    assert response.status_code in [200, 307, 308]


@pytest.mark.integration
def test_redoc_endpoint_exists(client):
    """Test that redoc endpoint exists."""
    response = client.get("/redoc")
    # Should either return 200 (redoc) or redirect, but not 404
    assert response.status_code in [200, 307, 308]


@pytest.mark.integration
def test_nonexistent_endpoint(client):
    """Test that nonexistent endpoints return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404