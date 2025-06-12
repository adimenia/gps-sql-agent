"""Unit tests for ETL transformers."""

import pytest
from datetime import datetime
from app.etl.transformers.activities import ActivityTransformer, OwnerExtractor
from app.etl.transformers.athletes import AthleteTransformer
from app.etl.transformers.events import EventTransformer
from app.etl.transformers.efforts import EffortTransformer


@pytest.mark.unit
@pytest.mark.etl
def test_activity_transformer():
    """Test activity data transformation."""
    transformer = ActivityTransformer()
    
    raw_activity = {
        "id": 12345,
        "name": "Training Session",
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
        "athlete_count": 2,
        "period_count": 1,
        "activity_athletes": ["1001", "1002"]
    }
    
    result = transformer.transform(raw_activity)
    
    assert len(result) == 1
    transformed = result[0]
    
    assert transformed["activity_id"] == 12345
    assert transformed["name"] == "Training Session"
    assert transformed["owner_id"] == 1
    assert transformed["owner_name"] == "Test Owner"
    assert transformed["athlete_count"] == 2


@pytest.mark.unit
@pytest.mark.etl
def test_activity_transformer_missing_required_fields():
    """Test activity transformer with missing required fields."""
    transformer = ActivityTransformer()
    
    # Missing required 'id' field
    raw_activity = {
        "name": "Training Session"
    }
    
    result = transformer.transform(raw_activity)
    assert result == []


@pytest.mark.unit
@pytest.mark.etl
def test_athlete_transformer():
    """Test athlete data transformation."""
    transformer = AthleteTransformer()
    
    raw_athlete = {
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
    
    result = transformer.transform(raw_athlete)
    
    assert len(result) == 1
    transformed = result[0]
    
    assert transformed["athlete_id"] == 1001
    assert transformed["first_name"] == "John"
    assert transformed["last_name"] == "Doe"
    assert transformed["jersey_number"] == 10
    assert transformed["height"] == 180.5
    assert transformed["date_of_birth"] == "1995-01-01"


@pytest.mark.unit
@pytest.mark.etl
def test_athlete_transformer_timestamp_date_of_birth():
    """Test athlete transformer with Unix timestamp date of birth."""
    transformer = AthleteTransformer()
    
    raw_athlete = {
        "id": 1001,
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": 788918400  # Unix timestamp for 1995-01-01
    }
    
    result = transformer.transform(raw_athlete)
    
    assert len(result) == 1
    transformed = result[0]
    
    assert transformed["athlete_id"] == 1001
    assert transformed["date_of_birth"] == "1995-01-01"


@pytest.mark.unit
@pytest.mark.etl
def test_event_transformer():
    """Test event data transformation."""
    transformer = EventTransformer()
    
    raw_event = {
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
                },
                {
                    "event_id": 100002,
                    "start_time": 1640995270,
                    "end_time": 1640995275,
                    "version": 1,
                    "intensity": "medium"
                }
            ]
        }
    }
    
    result = transformer.transform(raw_event, activity_id=12345, athlete_id=1001)
    
    assert len(result) == 2
    
    first_event = result[0]
    assert first_event["event_id"] == 100001
    assert first_event["activity_id"] == 12345
    assert first_event["athlete_id"] == 1001
    assert first_event["device_id"] == 5001
    assert first_event["intensity"] == "high"
    assert first_event["direction"] == "forward"
    
    second_event = result[1]
    assert second_event["event_id"] == 100002
    assert second_event["intensity"] == "medium"
    assert second_event["direction"] is None


@pytest.mark.unit
@pytest.mark.etl
def test_event_transformer_missing_context():
    """Test event transformer without required context."""
    transformer = EventTransformer()
    
    raw_event = {
        "device_id": 5001,
        "data": {"ima_acceleration": []}
    }
    
    # Missing activity_id and athlete_id
    result = transformer.transform(raw_event)
    assert result == []


@pytest.mark.unit
@pytest.mark.etl
def test_effort_transformer():
    """Test effort data transformation."""
    transformer = EffortTransformer()
    
    raw_effort = {
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
    
    result = transformer.transform(raw_effort, activity_id=12345, athlete_id=1001)
    
    assert len(result) == 2
    
    # Check velocity effort
    velocity_effort = result[0]
    assert velocity_effort["athlete_id"] == 1001
    assert velocity_effort["activity_id"] == 12345
    assert velocity_effort["device_id"] == 5001
    assert velocity_effort["band"] == "zone_4"
    assert velocity_effort["distance"] == 25.5
    assert velocity_effort["velocity"] == 7.2
    assert velocity_effort["acceleration"] is None
    
    # Check acceleration effort
    acceleration_effort = result[1]
    assert acceleration_effort["band"] == "zone_3"
    assert acceleration_effort["distance"] == 15.2
    assert acceleration_effort["velocity"] is None
    assert acceleration_effort["acceleration"] == 3.8


@pytest.mark.unit
@pytest.mark.etl
def test_owner_extractor():
    """Test owner extraction from activities."""
    activities = [
        {
            "id": 1,
            "owner": {
                "id": 100,
                "name": "Owner 1",
                "email": "owner1@example.com",
                "customer_id": "cust1",
                "default": True,
                "is_synced": True
            }
        },
        {
            "id": 2,
            "owner": {
                "id": 100,  # Same owner
                "name": "Owner 1",
                "email": "owner1@example.com"
            }
        },
        {
            "id": 3,
            "owner": {
                "id": 200,  # Different owner
                "name": "Owner 2",
                "email": "owner2@example.com"
            }
        }
    ]
    
    owners = OwnerExtractor.extract_owners(activities)
    
    # Should extract 2 unique owners
    assert len(owners) == 2
    
    owner_ids = [owner["owner_id"] for owner in owners]
    assert 100 in owner_ids
    assert 200 in owner_ids


@pytest.mark.unit
@pytest.mark.etl
def test_base_transformer_helpers():
    """Test base transformer helper methods."""
    from app.etl.transformers.base import BaseTransformer
    
    class TestTransformer(BaseTransformer):
        def transform(self, raw_data):
            return []
    
    transformer = TestTransformer()
    
    # Test timestamp transformation
    dt = transformer.transform_timestamp(1640995200)
    assert isinstance(dt, datetime)
    assert dt.year == 2022
    
    # Test invalid timestamp
    dt = transformer.transform_timestamp("invalid")
    assert dt is None
    
    # Test safe_bool
    assert transformer.safe_bool(True) is True
    assert transformer.safe_bool("true") is True
    assert transformer.safe_bool("false") is False
    assert transformer.safe_bool(1) is True
    assert transformer.safe_bool(0) is False
    assert transformer.safe_bool(None) is None
    
    # Test safe_int
    assert transformer.safe_int("123") == 123
    assert transformer.safe_int("invalid") is None
    assert transformer.safe_int(None) is None
    
    # Test safe_float
    assert transformer.safe_float("123.45") == 123.45
    assert transformer.safe_float("invalid") is None
    assert transformer.safe_float(None) is None