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
        """Load effort data into database with application-level duplicate prevention."""
        if not data:
            return 0
        
        try:
            # Filter out duplicates before insertion using application logic
            unique_efforts = self._filter_duplicates(data)
            
            if not unique_efforts:
                logger.info("No new effort records to insert (all were duplicates)")
                return 0
            
            # Use bulk insert for the filtered unique data
            from sqlalchemy.dialects.postgresql import insert
            
            stmt = insert(Effort.__table__).values(unique_efforts)
            # Still use on_conflict_do_nothing as a safety net
            stmt = stmt.on_conflict_do_nothing()
            
            result = self.db.execute(stmt)
            self.db.commit()
            
            logger.info(f"✅ Inserted {len(unique_efforts)} new effort records (filtered out {len(data) - len(unique_efforts)} duplicates)")
            return len(unique_efforts)
            
        except Exception as e:
            logger.error(f"❌ Error inserting efforts: {e}")
            self.db.rollback()
            return 0
    
    def _filter_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out duplicate efforts based on natural key combination."""
        if not data:
            return []
        
        try:
            # Get existing efforts' natural keys from database
            from sqlalchemy import and_
            
            # Build a set of natural keys to check against
            natural_keys_to_check = set()
            for effort in data:
                natural_key = (
                    effort.get('activity_id'),
                    effort.get('athlete_id'), 
                    effort.get('start_time'),
                    effort.get('end_time'),
                    effort.get('effort_type', ''),
                    effort.get('band', '')
                )
                natural_keys_to_check.add(natural_key)
            
            # Query existing efforts that match any of these natural keys
            existing_efforts = self.db.query(
                Effort.activity_id,
                Effort.athlete_id,
                Effort.start_time,
                Effort.end_time,
                Effort.effort_type,
                Effort.band
            ).filter(
                and_(
                    Effort.activity_id.in_([key[0] for key in natural_keys_to_check if key[0]]),
                    Effort.athlete_id.in_([key[1] for key in natural_keys_to_check if key[1]])
                )
            ).all()
            
            # Create set of existing natural keys
            existing_keys = set()
            for effort in existing_efforts:
                natural_key = (
                    effort.activity_id,
                    effort.athlete_id,
                    effort.start_time,
                    effort.end_time,
                    effort.effort_type or '',
                    effort.band or ''
                )
                existing_keys.add(natural_key)
            
            # Filter out duplicates
            unique_efforts = []
            for effort in data:
                natural_key = (
                    effort.get('activity_id'),
                    effort.get('athlete_id'),
                    effort.get('start_time'),
                    effort.get('end_time'),
                    effort.get('effort_type', ''),
                    effort.get('band', '')
                )
                
                if natural_key not in existing_keys:
                    unique_efforts.append(effort)
                    existing_keys.add(natural_key)  # Prevent within-batch duplicates too
            
            return unique_efforts
            
        except Exception as e:
            logger.warning(f"Error filtering duplicates, proceeding with all data: {e}")
            return data


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