"""Unit tests for configuration."""

import pytest
import os
from unittest.mock import patch

from app.core.config import Settings


@pytest.mark.unit
def test_default_settings():
    """Test default configuration values."""
    settings = Settings()
    
    assert settings.postgres_host == "localhost"
    assert settings.postgres_port == 5433  # Using port from .env file
    assert settings.postgres_db == "sports_analytics"
    assert settings.postgres_user == "postgres"
    assert settings.app_env == "development"
    assert settings.debug is True
    assert settings.api_port == 8000


@pytest.mark.unit
def test_database_url_construction():
    """Test database URL construction."""
    settings = Settings(
        postgres_user="testuser",
        postgres_password="testpass",
        postgres_host="testhost",
        postgres_port=5433,
        postgres_db="testdb"
    )
    
    expected_url = "postgresql://testuser:testpass@testhost:5433/testdb"
    assert settings.database_url == expected_url


@pytest.mark.unit
def test_async_database_url_construction():
    """Test async database URL construction."""
    settings = Settings(
        postgres_user="testuser",
        postgres_password="testpass",
        postgres_host="testhost",
        postgres_port=5433,
        postgres_db="testdb"
    )
    
    expected_url = "postgresql+asyncpg://testuser:testpass@testhost:5433/testdb"
    assert settings.async_database_url == expected_url


@pytest.mark.unit
def test_catapult_headers_construction():
    """Test Catapult API headers construction."""
    settings = Settings(catapult_api_token="test_token_123")
    
    expected_headers = {
        "accept": "application/json",
        "authorization": "Bearer test_token_123"
    }
    assert settings.catapult_headers == expected_headers


@pytest.mark.unit
def test_environment_variable_override():
    """Test that environment variables override defaults."""
    with patch.dict(os.environ, {
        'POSTGRES_HOST': 'env_host',
        'POSTGRES_PORT': '9999',
        'POSTGRES_DB': 'env_db',
        'DEBUG': 'false',
        'APP_ENV': 'production'
    }):
        settings = Settings()
        
        assert settings.postgres_host == "env_host"
        assert settings.postgres_port == 9999
        assert settings.postgres_db == "env_db"
        assert settings.debug is False
        assert settings.app_env == "production"


@pytest.mark.unit
def test_catapult_api_settings():
    """Test Catapult API related settings."""
    settings = Settings(
        catapult_api_url="https://test-api.example.com",
        catapult_api_token="test_token"
    )
    
    assert settings.catapult_api_url == "https://test-api.example.com"
    assert settings.catapult_api_token == "test_token"


@pytest.mark.unit
def test_etl_settings():
    """Test ETL related settings."""
    settings = Settings(
        etl_schedule_hours=12,
        etl_batch_size=200
    )
    
    assert settings.etl_schedule_hours == 12
    assert settings.etl_batch_size == 200