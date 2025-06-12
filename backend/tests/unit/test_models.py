"""Unit tests for database models."""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.sports import Activity, Athlete, Position, Owner, Event, Effort


@pytest.mark.unit
def test_create_activity(test_db_session):
    """Test creating an activity."""
    activity = Activity(
        activity_id=12345,
        name="Test Training Session",
        start_time=datetime(2022, 1, 1, 10, 0, 0),
        end_time=datetime(2022, 1, 1, 11, 0, 0),
        athlete_count=5,
        period_count=2
    )
    
    test_db_session.add(activity)
    test_db_session.commit()
    
    # Verify the activity was created
    retrieved_activity = test_db_session.query(Activity).filter(
        Activity.activity_id == 12345
    ).first()
    
    assert retrieved_activity is not None
    assert retrieved_activity.name == "Test Training Session"
    assert retrieved_activity.athlete_count == 5


@pytest.mark.unit
def test_create_athlete(test_db_session):
    """Test creating an athlete."""
    athlete = Athlete(
        athlete_id=1001,
        first_name="John",
        last_name="Doe",
        gender="Male",
        jersey_number=10,
        height=180.5,
        weight=75.2
    )
    
    test_db_session.add(athlete)
    test_db_session.commit()
    
    # Verify the athlete was created
    retrieved_athlete = test_db_session.query(Athlete).filter(
        Athlete.athlete_id == 1001
    ).first()
    
    assert retrieved_athlete is not None
    assert retrieved_athlete.first_name == "John"
    assert retrieved_athlete.last_name == "Doe"
    assert retrieved_athlete.jersey_number == 10


@pytest.mark.unit
def test_athlete_activity_relationship(test_db_session):
    """Test relationship between athlete and activity through events."""
    # Create activity
    activity = Activity(
        activity_id=12345,
        name="Test Session",
        start_time=datetime(2022, 1, 1, 10, 0, 0),
        end_time=datetime(2022, 1, 1, 11, 0, 0)
    )
    
    # Create athlete
    athlete = Athlete(
        athlete_id=1001,
        first_name="John",
        last_name="Doe"
    )
    
    # Create event linking them
    event = Event(
        event_id=100001,
        activity_id=12345,
        athlete_id=1001,
        device_id=5001,
        start_time=datetime(2022, 1, 1, 10, 5, 0),
        end_time=datetime(2022, 1, 1, 10, 5, 5)
    )
    
    test_db_session.add_all([activity, athlete, event])
    test_db_session.commit()
    
    # Test relationships
    retrieved_event = test_db_session.query(Event).first()
    assert retrieved_event.activity.name == "Test Session"
    assert retrieved_event.athlete.first_name == "John"


@pytest.mark.unit
def test_position_athlete_relationship(test_db_session):
    """Test relationship between position and athlete."""
    # Create position
    position = Position(
        position_id=1,
        name="Forward",
        slug="forward",
        sport_id=1,
        sport_name="Football"
    )
    
    # Create athlete with position
    athlete = Athlete(
        athlete_id=1001,
        first_name="John",
        last_name="Doe",
        position_id=1
    )
    
    test_db_session.add_all([position, athlete])
    test_db_session.commit()
    
    # Test relationship
    retrieved_athlete = test_db_session.query(Athlete).first()
    assert retrieved_athlete.position.name == "Forward"
    assert retrieved_athlete.position.sport_name == "Football"


@pytest.mark.unit
def test_effort_creation(test_db_session):
    """Test creating an effort record."""
    # Create required parent records
    activity = Activity(
        activity_id=12345,
        name="Test Session",
        start_time=datetime(2022, 1, 1, 10, 0, 0),
        end_time=datetime(2022, 1, 1, 11, 0, 0)
    )
    
    athlete = Athlete(
        athlete_id=1001,
        first_name="John",
        last_name="Doe"
    )
    
    effort = Effort(
        athlete_id=1001,
        activity_id=12345,
        device_id=5001,
        start_time=datetime(2022, 1, 1, 10, 5, 0),
        end_time=datetime(2022, 1, 1, 10, 5, 10),
        band="zone_4",
        distance=25.5,
        velocity=7.2
    )
    
    test_db_session.add_all([activity, athlete, effort])
    test_db_session.commit()
    
    # Verify effort was created with relationships
    retrieved_effort = test_db_session.query(Effort).first()
    assert retrieved_effort.band == "zone_4"
    assert retrieved_effort.distance == 25.5
    assert retrieved_effort.velocity == 7.2
    assert retrieved_effort.athlete.first_name == "John"
    assert retrieved_effort.activity.name == "Test Session"


@pytest.mark.unit
def test_owner_activity_relationship(test_db_session):
    """Test relationship between owner and activities."""
    # Create owner
    owner = Owner(
        owner_id=1,
        name="Test Owner",
        email="test@example.com",
        customer_id="test-customer"
    )
    
    # Create activity with owner
    activity = Activity(
        activity_id=12345,
        name="Test Session",
        owner_id=1,
        start_time=datetime(2022, 1, 1, 10, 0, 0),
        end_time=datetime(2022, 1, 1, 11, 0, 0)
    )
    
    test_db_session.add_all([owner, activity])
    test_db_session.commit()
    
    # Test relationship
    retrieved_activity = test_db_session.query(Activity).first()
    assert retrieved_activity.owner.name == "Test Owner"
    assert retrieved_activity.owner.email == "test@example.com"


@pytest.mark.unit
def test_model_timestamps(test_db_session):
    """Test that timestamps are automatically set."""
    activity = Activity(
        activity_id=12345,
        name="Test Session",
        start_time=datetime(2022, 1, 1, 10, 0, 0),
        end_time=datetime(2022, 1, 1, 11, 0, 0)
    )
    
    test_db_session.add(activity)
    test_db_session.commit()
    
    # Verify timestamps were set
    retrieved_activity = test_db_session.query(Activity).first()
    assert retrieved_activity.created_at is not None
    assert retrieved_activity.updated_at is not None


@pytest.mark.unit
def test_duplicate_primary_key_fails(test_db_session):
    """Test that duplicate primary keys raise an error."""
    activity1 = Activity(
        activity_id=12345,
        name="First Session"
    )
    
    activity2 = Activity(
        activity_id=12345,  # Same ID
        name="Second Session"
    )
    
    test_db_session.add(activity1)
    test_db_session.commit()
    
    # Adding duplicate should fail
    test_db_session.add(activity2)
    with pytest.raises(IntegrityError):
        test_db_session.commit()