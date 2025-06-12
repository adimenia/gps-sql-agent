"""Loaders for sports-specific data."""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.sports import Activity, Athlete, Event, Effort, Position, Parameter, Period, Owner
from .base import BaseLoader
import logging

logger = logging.getLogger(__name__)


class ActivityLoader(BaseLoader):
    """Loader for activity data."""
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load activity data into database."""
        return self.bulk_insert_on_conflict_ignore(Activity.__table__, data)


class AthleteLoader(BaseLoader):
    """Loader for athlete data."""
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load athlete data into database."""
        # Use upsert for athletes to update their information
        update_columns = [
            'first_name', 'last_name', 'gender', 'jersey_number',
            'height', 'weight', 'position_id', 'date_of_birth'
        ]
        return self.bulk_upsert(
            Athlete.__table__, 
            data, 
            conflict_columns=['athlete_id'],
            update_columns=update_columns
        )


class EventLoader(BaseLoader):
    """Loader for event data."""
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load event data into database."""
        return self.bulk_insert_on_conflict_ignore(Event.__table__, data)


class EffortLoader(BaseLoader):
    """Loader for effort data."""
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load effort data into database."""
        # Efforts table has a serial primary key, so we use a different approach
        if not data:
            return 0
        
        try:
            # For efforts, we'll do a simple insert and let duplicates be handled by the app logic
            # since efforts don't have a natural unique key besides the serial id
            for effort_data in data:
                effort = Effort(**effort_data)
                self.db.add(effort)
            
            self.db.commit()
            logger.info(f"Inserted {len(data)} effort records")
            return len(data)
            
        except Exception as e:
            logger.error(f"Error inserting efforts: {e}")
            self.db.rollback()
            return 0


class PositionLoader(BaseLoader):
    """Loader for position data."""
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load position data into database."""
        return self.bulk_insert_on_conflict_ignore(Position.__table__, data)


class ParameterLoader(BaseLoader):
    """Loader for parameter data."""
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load parameter data into database."""
        return self.bulk_insert_on_conflict_ignore(Parameter.__table__, data)


class PeriodLoader(BaseLoader):
    """Loader for period data."""
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load period data into database."""
        return self.bulk_insert_on_conflict_ignore(Period.__table__, data)


class OwnerLoader(BaseLoader):
    """Loader for owner data."""
    
    def load(self, data: List[Dict[str, Any]]) -> int:
        """Load owner data into database."""
        return self.bulk_insert_on_conflict_ignore(Owner.__table__, data)


class LoaderFactory:
    """Factory for creating appropriate loaders."""
    
    @staticmethod
    def get_loader(data_type: str, db_session: Session) -> BaseLoader:
        """Get appropriate loader for data type."""
        loaders = {
            'activities': ActivityLoader,
            'athletes': AthleteLoader,
            'events': EventLoader,
            'efforts': EffortLoader,
            'positions': PositionLoader,
            'parameters': ParameterLoader,
            'periods': PeriodLoader,
            'owners': OwnerLoader
        }
        
        loader_class = loaders.get(data_type)
        if not loader_class:
            raise ValueError(f"Unknown data type: {data_type}")
        
        return loader_class(db_session)