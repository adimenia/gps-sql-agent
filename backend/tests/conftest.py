"""Global test configuration and fixtures."""

import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Add the parent directory to Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app
from app.models.base import Base
from app.core.database import get_database_session
from app.core.config import settings


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine."""
    # Use SQLite for testing for simplicity
    test_db_url = "sqlite:///./test.db"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(test_db_session):
    """Create a test client with database dependency override."""
    
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_database_session] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_catapult_api():
    """Mock Catapult API responses."""
    mock = MagicMock()
    
    # Sample activity data
    mock.fetch_activities.return_value = [
        {
            "id": 12345,
            "name": "Test Training Session",
            "start_time": 1640995200,  # 2022-01-01 00:00:00
            "end_time": 1640998800,    # 2022-01-01 01:00:00
            "game_id": None,
            "owner": {
                "id": 1,
                "customer_id": "test-customer",
                "name": "Test Owner",
                "email": "test@example.com",
                "is_synced": True,
                "is_deleted": False,
                "created_at": "2022-01-01T00:00:00Z",
                "modified_at": "2022-01-01T00:00:00Z",
                "default": False,
                "software_version": {"version": "1.0.0"}
            },
            "periods": [],
            "tags": [],
            "tag_list": [],
            "athlete_count": 2,
            "period_count": 1,
            "activity_athletes": ["1001", "1002"]
        }
    ]
    
    # Sample athlete data
    mock.fetch_athletes.return_value = [
        {
            "id": 1001,
            "first_name": "John",
            "last_name": "Doe",
            "gender": "Male",
            "jersey": 10,
            "height": 180.5,
            "weight": 75.2,
            "position_id": 1,
            "date_of_birth_date": "1995-01-01",
            "velocity_max": 8.5,
            "acceleration_max": 4.2,
            "heart_rate_max": 190
        },
        {
            "id": 1002,
            "first_name": "Jane",
            "last_name": "Smith",
            "gender": "Female",
            "jersey": 7,
            "height": 165.0,
            "weight": 60.5,
            "position_id": 2,
            "date_of_birth_date": "1997-03-15",
            "velocity_max": 7.8,
            "acceleration_max": 3.9,
            "heart_rate_max": 185
        }
    ]
    
    return mock


@pytest.fixture
def sample_activity_data():
    """Sample activity data for testing."""
    return {
        "id": 12345,
        "name": "Test Training Session",
        "start_time": 1640995200,
        "end_time": 1640998800,
        "game_id": None,
        "owner": {
            "id": 1,
            "customer_id": "test-customer",
            "name": "Test Owner",
            "email": "test@example.com",
            "is_synced": True,
            "is_deleted": False,
            "created_at": "2022-01-01T00:00:00Z",
            "modified_at": "2022-01-01T00:00:00Z",
            "default": False,
            "software_version": {"version": "1.0.0"}
        },
        "periods": [],
        "tags": [],
        "tag_list": [],
        "athlete_count": 2,
        "period_count": 1,
        "activity_athletes": ["1001", "1002"]
    }


@pytest.fixture
def sample_athlete_data():
    """Sample athlete data for testing."""
    return [
        {
            "id": 1001,
            "first_name": "John",
            "last_name": "Doe",
            "gender": "Male",
            "jersey": 10,
            "height": 180.5,
            "weight": 75.2,
            "position_id": 1,
            "date_of_birth_date": "1995-01-01"
        }
    ]


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return [
        {
            "device_id": 5001,
            "data": {
                "ima_acceleration": [
                    {
                        "event_id": 100001,
                        "start_time": 1640995260,
                        "end_time": 1640995265,
                        "version": 1,
                        "intensity": "high",
                        "direction": "forward"
                    }
                ]
            }
        }
    ]


@pytest.fixture
def sample_effort_data():
    """Sample effort data for testing."""
    return [
        {
            "device_id": 5001,
            "data": {
                "velocity_efforts": [
                    {
                        "start_time": 1640995300,
                        "end_time": 1640995310,
                        "band": "zone_4",
                        "distance": 25.5,
                        "max_velocity": 7.2
                    }
                ],
                "acceleration_efforts": [
                    {
                        "start_time": 1640995320,
                        "end_time": 1640995325,
                        "band": "zone_3", 
                        "distance": 15.2,
                        "acceleration": 3.8
                    }
                ]
            }
        }
    ]


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup test files after each test."""
    yield
    
    # Clean up any test log files
    test_files = ["test.log", "data_ingestion.log"]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)