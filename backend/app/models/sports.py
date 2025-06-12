from sqlalchemy import Column, Integer, BigInteger, String, Boolean, TIMESTAMP, DECIMAL, Date, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

# Use JSON for SQLite compatibility in tests, JSONB for PostgreSQL in production
def get_json_type():
    """Return appropriate JSON type based on database."""
    # This will be JSONB in PostgreSQL, JSON in SQLite
    return JSON


class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    game_id = Column(BigInteger)
    owner_id = Column(BigInteger, ForeignKey("owners.owner_id"))
    owner_customer_id = Column(String(255))
    owner_name = Column(String(255))
    owner_email = Column(String(255))
    owner_is_synced = Column(Boolean)
    owner_is_deleted = Column(Boolean)
    owner_created_at = Column(TIMESTAMP)
    owner_modified_at = Column(TIMESTAMP)
    owner_default = Column(Boolean)
    owner_software_version = Column(get_json_type())
    periods = Column(get_json_type())
    tags = Column(get_json_type())
    tag_list = Column(get_json_type())
    athlete_count = Column(Integer)
    period_count = Column(Integer)
    activity_athletes = Column(get_json_type())
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("Owner", back_populates="activities")
    periods_rel = relationship("Period", back_populates="activity")
    events = relationship("Event", back_populates="activity")
    efforts = relationship("Effort", back_populates="activity")


class Athlete(Base):
    __tablename__ = "athletes"

    athlete_id = Column(BigInteger, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    gender = Column(String(10))
    jersey_number = Column(Integer)
    height = Column(DECIMAL(5, 2))
    weight = Column(DECIMAL(5, 2))
    position_id = Column(BigInteger, ForeignKey("positions.position_id"))
    date_of_birth = Column(Date)
    velocity_max = Column(DECIMAL(5, 2))
    acceleration_max = Column(DECIMAL(5, 2))
    heart_rate_max = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    position = relationship("Position", back_populates="athletes")
    events = relationship("Event", back_populates="athlete")
    efforts = relationship("Effort", back_populates="athlete")


class Position(Base):
    __tablename__ = "positions"

    position_id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    slug = Column(String(255))
    sport_id = Column(BigInteger)
    sport_name = Column(String(255))
    created_at = Column(TIMESTAMP)
    modified_at = Column(TIMESTAMP)

    # Relationships
    athletes = relationship("Athlete", back_populates="position")


class Parameter(Base):
    __tablename__ = "parameters"

    parameter_id = Column(BigInteger, primary_key=True)
    parameter_type_id = Column(BigInteger)
    name = Column(String(255))
    original_name = Column(String(255))
    slug = Column(String(255))
    calculation = Column(Text)
    ctr_order = Column(Integer)
    created_at = Column(TIMESTAMP)
    modified_at = Column(TIMESTAMP)
    unit_type = Column(String(255))


class Period(Base):
    __tablename__ = "periods"

    period_id = Column(BigInteger, primary_key=True)
    activity_id = Column(BigInteger, ForeignKey("activities.activity_id"))
    name = Column(String(255))
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP)
    modified_at = Column(TIMESTAMP)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    activity = relationship("Activity", back_populates="periods_rel")


class Event(Base):
    __tablename__ = "events"

    event_id = Column(BigInteger, primary_key=True)
    activity_id = Column(BigInteger, ForeignKey("activities.activity_id"))
    athlete_id = Column(BigInteger, ForeignKey("athletes.athlete_id"))
    device_id = Column(BigInteger)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    version = Column(Integer)
    intensity = Column(String(255))
    direction = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    activity = relationship("Activity", back_populates="events")
    athlete = relationship("Athlete", back_populates="events")


class Effort(Base):
    __tablename__ = "efforts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    athlete_id = Column(BigInteger, ForeignKey("athletes.athlete_id"))
    activity_id = Column(BigInteger, ForeignKey("activities.activity_id"))
    device_id = Column(BigInteger)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    band = Column(String(255))
    distance = Column(DECIMAL(10, 2))
    velocity = Column(DECIMAL(5, 2))
    acceleration = Column(DECIMAL(5, 2))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    athlete = relationship("Athlete", back_populates="efforts")
    activity = relationship("Activity", back_populates="efforts")


class Owner(Base):
    __tablename__ = "owners"

    owner_id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    customer_id = Column(String(255))
    default_flag = Column(Boolean)
    is_synced = Column(Boolean)
    created_at = Column(TIMESTAMP)
    modified_at = Column(TIMESTAMP)
    software_version = Column(get_json_type())

    # Relationships
    activities = relationship("Activity", back_populates="owner")