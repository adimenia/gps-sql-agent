"""Test utilities and helpers."""

import json
from datetime import datetime
from typing import Dict, Any, List

from app.models.sports import Activity, Athlete, Event, Effort


def create_test_activity(
    activity_id: int = 12345,
    name: str = "Test Activity",
    **kwargs
) -> Activity:
    """Create a test activity with reasonable defaults."""
    defaults = {
        "start_time": datetime(2022, 1, 1, 10, 0, 0),
        "end_time": datetime(2022, 1, 1, 11, 0, 0),
        "athlete_count": 1,
        "period_count": 1
    }
    defaults.update(kwargs)
    
    return Activity(
        activity_id=activity_id,
        name=name,
        **defaults
    )


def create_test_athlete(
    athlete_id: int = 1001,
    first_name: str = "Test",
    last_name: str = "Athlete",
    **kwargs
) -> Athlete:
    """Create a test athlete with reasonable defaults."""
    defaults = {
        "gender": "Male",
        "jersey_number": 10,
        "height": 180.0,
        "weight": 75.0
    }
    defaults.update(kwargs)
    
    return Athlete(
        athlete_id=athlete_id,
        first_name=first_name,
        last_name=last_name,
        **defaults
    )


def create_test_event(
    event_id: int = 100001,
    activity_id: int = 12345,
    athlete_id: int = 1001,
    **kwargs
) -> Event:
    """Create a test event with reasonable defaults."""
    defaults = {
        "device_id": 5001,
        "start_time": datetime(2022, 1, 1, 10, 5, 0),
        "end_time": datetime(2022, 1, 1, 10, 5, 5),
        "version": 1,
        "intensity": "medium"
    }
    defaults.update(kwargs)
    
    return Event(
        event_id=event_id,
        activity_id=activity_id,
        athlete_id=athlete_id,
        **defaults
    )


def create_test_effort(
    activity_id: int = 12345,
    athlete_id: int = 1001,
    **kwargs
) -> Effort:
    """Create a test effort with reasonable defaults."""
    defaults = {
        "device_id": 5001,
        "start_time": datetime(2022, 1, 1, 10, 5, 0),
        "end_time": datetime(2022, 1, 1, 10, 5, 10),
        "band": "zone_3",
        "distance": 20.0,
        "velocity": 6.5
    }
    defaults.update(kwargs)
    
    return Effort(
        activity_id=activity_id,
        athlete_id=athlete_id,
        **defaults
    )


def mock_catapult_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create a mock response object for Catapult API."""
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            
        def json(self):
            return self.json_data
            
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")
    
    return MockResponse(data, status_code)


def assert_activity_matches_data(activity: Activity, data: Dict[str, Any]):
    """Assert that an Activity model matches the source data."""
    assert activity.activity_id == data["id"]
    assert activity.name == data["name"]
    assert activity.athlete_count == data.get("athlete_count", 0)
    assert activity.period_count == data.get("period_count", 0)


def assert_athlete_matches_data(athlete: Athlete, data: Dict[str, Any]):
    """Assert that an Athlete model matches the source data."""
    assert athlete.athlete_id == data["id"]
    assert athlete.first_name == data.get("first_name")
    assert athlete.last_name == data.get("last_name")
    assert athlete.gender == data.get("gender")
    assert athlete.jersey_number == data.get("jersey")


def generate_sample_api_data() -> Dict[str, Any]:
    """Generate sample data that mimics Catapult API responses."""
    return {
        "activities": [
            {
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
                "periods": [],
                "tags": [],
                "tag_list": [],
                "athlete_count": 2,
                "period_count": 1,
                "activity_athletes": ["1001", "1002"]
            }
        ],
        "athletes": [
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
                "date_of_birth_date": "1997-03-15"
            }
        ],
        "events": [
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
        ],
        "efforts": [
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
                    ]
                }
            }
        ]
    }