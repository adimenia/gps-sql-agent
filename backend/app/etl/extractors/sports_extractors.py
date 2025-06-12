"""Extractors for sports-specific data."""

from typing import List, Dict, Any, Optional
from .base import BaseExtractor
import logging

logger = logging.getLogger(__name__)


class ActivityExtractor(BaseExtractor):
    """Extractor for activity data."""
    
    async def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract all activities."""
        logger.info("Extracting activities")
        activities = await self.client.fetch_activities()
        
        if not self.validate_response(activities):
            return []
        
        logger.info(f"Extracted {len(activities)} activities")
        return activities


class AthleteExtractor(BaseExtractor):
    """Extractor for athlete data."""
    
    async def extract(self, activity_id: int = None, **kwargs) -> List[Dict[str, Any]]:
        """Extract athletes for a specific activity."""
        if not activity_id:
            logger.error("activity_id is required for athlete extraction")
            return []
        
        logger.debug(f"Extracting athletes for activity {activity_id}")
        athletes = await self.client.fetch_athletes(activity_id)
        
        if not self.validate_response(athletes):
            return []
        
        logger.debug(f"Extracted {len(athletes)} athletes for activity {activity_id}")
        return athletes


class EventExtractor(BaseExtractor):
    """Extractor for event data."""
    
    async def extract(self, activity_id: int = None, athlete_id: int = None, event_types: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Extract events for a specific activity and athlete."""
        if not activity_id or not athlete_id:
            logger.error("activity_id and athlete_id are required for event extraction")
            return []
        
        logger.debug(f"Extracting events for activity {activity_id}, athlete {athlete_id}")
        events = await self.client.fetch_events(activity_id, athlete_id, event_types)
        
        if not self.validate_response(events):
            return []
        
        logger.debug(f"Extracted {len(events)} event records for activity {activity_id}, athlete {athlete_id}")
        return events


class EffortExtractor(BaseExtractor):
    """Extractor for effort data."""
    
    async def extract(self, activity_id: int = None, athlete_id: int = None, effort_types: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Extract efforts for a specific activity and athlete."""
        if not activity_id or not athlete_id:
            logger.error("activity_id and athlete_id are required for effort extraction")
            return []
        
        logger.debug(f"Extracting efforts for activity {activity_id}, athlete {athlete_id}")
        efforts = await self.client.fetch_efforts(activity_id, athlete_id, effort_types)
        
        if not self.validate_response(efforts):
            return []
        
        logger.debug(f"Extracted {len(efforts)} effort records for activity {activity_id}, athlete {athlete_id}")
        return efforts


class PositionExtractor(BaseExtractor):
    """Extractor for position data."""
    
    async def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract all positions."""
        logger.info("Extracting positions")
        positions = await self.client.fetch_positions()
        
        if not self.validate_response(positions):
            return []
        
        logger.info(f"Extracted {len(positions)} positions")
        return positions


class ParameterExtractor(BaseExtractor):
    """Extractor for parameter data."""
    
    async def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """Extract all parameters."""
        logger.info("Extracting parameters")
        parameters = await self.client.fetch_parameters()
        
        if not self.validate_response(parameters):
            return []
        
        logger.info(f"Extracted {len(parameters)} parameters")
        return parameters


class PeriodExtractor(BaseExtractor):
    """Extractor for period data."""
    
    async def extract(self, activity_id: int = None, **kwargs) -> List[Dict[str, Any]]:
        """Extract periods for a specific activity."""
        if not activity_id:
            logger.error("activity_id is required for period extraction")
            return []
        
        logger.debug(f"Extracting periods for activity {activity_id}")
        periods = await self.client.fetch_periods(activity_id)
        
        if not self.validate_response(periods):
            return []
        
        logger.debug(f"Extracted {len(periods)} periods for activity {activity_id}")
        return periods


class ExtractorFactory:
    """Factory for creating appropriate extractors."""
    
    @staticmethod
    def get_extractor(data_type: str, client) -> BaseExtractor:
        """Get appropriate extractor for data type."""
        extractors = {
            'activities': ActivityExtractor,
            'athletes': AthleteExtractor,
            'events': EventExtractor,
            'efforts': EffortExtractor,
            'positions': PositionExtractor,
            'parameters': ParameterExtractor,
            'periods': PeriodExtractor
        }
        
        extractor_class = extractors.get(data_type)
        if not extractor_class:
            raise ValueError(f"Unknown data type: {data_type}")
        
        return extractor_class(client)