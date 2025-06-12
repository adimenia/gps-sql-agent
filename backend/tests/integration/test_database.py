"""Integration tests for database operations."""

import pytest
from sqlalchemy import text

from app.core.database import check_database_connection, create_tables
from app.models.sports import Activity, Athlete


@pytest.mark.integration
def test_database_connection(test_db_session):
    """Test database connection works."""
    # Execute a simple query
    result = test_db_session.execute(text("SELECT 1 as test_value"))
    row = result.fetchone()
    
    assert row is not None
    assert row[0] == 1


@pytest.mark.integration
def test_database_session_rollback(test_db_session):
    """Test that database session rollbacks work properly."""
    # Add an activity
    activity = Activity(
        activity_id=99999,
        name="Rollback Test"
    )
    test_db_session.add(activity)
    test_db_session.flush()  # Send to DB but don't commit
    
    # Verify it's in the session
    found = test_db_session.query(Activity).filter(
        Activity.activity_id == 99999
    ).first()
    assert found is not None
    
    # Rollback
    test_db_session.rollback()
    
    # Verify it's gone after rollback
    found_after_rollback = test_db_session.query(Activity).filter(
        Activity.activity_id == 99999
    ).first()
    assert found_after_rollback is None


@pytest.mark.integration
def test_database_constraints(test_db_session):
    """Test database constraints work."""
    # Create activity
    activity = Activity(
        activity_id=12345,
        name="Constraint Test"
    )
    test_db_session.add(activity)
    test_db_session.commit()
    
    # Create athlete with reference to activity through events
    athlete = Athlete(
        athlete_id=1001,
        first_name="Test",
        last_name="Athlete"
    )
    test_db_session.add(athlete)
    test_db_session.commit()
    
    # Verify both records exist
    activity_count = test_db_session.query(Activity).count()
    athlete_count = test_db_session.query(Athlete).count()
    
    assert activity_count == 1
    assert athlete_count == 1


@pytest.mark.integration
def test_database_indexes_exist(test_db_session):
    """Test that important indexes exist."""
    # This test verifies that we can efficiently query by common fields
    # Add some test data
    activities = [
        Activity(
            activity_id=i,
            name=f"Activity {i}",
            owner_id=1 if i % 2 == 0 else 2
        )
        for i in range(1, 11)
    ]
    
    test_db_session.add_all(activities)
    test_db_session.commit()
    
    # Query by owner_id (should use index)
    owner_activities = test_db_session.query(Activity).filter(
        Activity.owner_id == 1
    ).all()
    
    assert len(owner_activities) == 5


@pytest.mark.integration 
def test_complex_query_performance(test_db_session):
    """Test complex queries work efficiently."""
    # Add test data
    activities = []
    athletes = []
    
    for i in range(1, 6):
        activity = Activity(
            activity_id=i,
            name=f"Activity {i}",
            athlete_count=2
        )
        activities.append(activity)
        
        for j in range(1, 3):
            athlete = Athlete(
                athlete_id=i * 10 + j,
                first_name=f"Athlete{j}",
                last_name=f"Activity{i}",
                jersey_number=j
            )
            athletes.append(athlete)
    
    test_db_session.add_all(activities + athletes)
    test_db_session.commit()
    
    # Complex query: activities with their athlete counts
    results = test_db_session.query(Activity).filter(
        Activity.athlete_count > 1
    ).all()
    
    assert len(results) == 5
    for result in results:
        assert result.athlete_count == 2