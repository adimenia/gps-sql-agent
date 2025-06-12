"""Event data transformer."""

from typing import Dict, List, Any
from .base import BaseTransformer
import logging

logger = logging.getLogger(__name__)


class EventTransformer(BaseTransformer):
    """Transform raw event data for database insertion."""
    
    def transform(self, raw_event: Dict[str, Any], activity_id: int = None, athlete_id: int = None) -> List[Dict[str, Any]]:
        """Transform event data from API response."""
        if not activity_id or not athlete_id:
            logger.error("activity_id and athlete_id are required for event transformation")
            return []
        
        transformed_events = []
        device_id = raw_event.get("device_id")
        event_data = raw_event.get("data", {})
        
        # Process each event type
        for event_type, event_list in event_data.items():
            if not isinstance(event_list, list):
                logger.warning(f"Expected list for event type {event_type}, got {type(event_list)}")
                continue
            
            for event_detail in event_list:
                event_id = event_detail.get("event_id")
                if not event_id:
                    logger.warning(f"Missing event_id in {event_type} event")
                    continue
                
                try:
                    transformed = {
                        "event_id": event_id,
                        "activity_id": activity_id,
                        "athlete_id": athlete_id,
                        "device_id": device_id,
                        "start_time": self.transform_timestamp(event_detail.get("start_time")),
                        "end_time": self.transform_timestamp(event_detail.get("end_time")),
                        "version": self.safe_int(event_detail.get("version")),
                        "intensity": self.safe_get(event_detail, "intensity"),
                        "direction": self.safe_get(event_detail, "direction")
                    }
                    
                    transformed_events.append(transformed)
                    logger.debug(f"Transformed event {event_id} for activity {activity_id}, athlete {athlete_id}")
                    
                except Exception as e:
                    logger.error(f"Error transforming event {event_id}: {e}")
                    continue
        
        return transformed_events


class EventBatchProcessor:
    """Process events in batches for multiple athletes."""
    
    def __init__(self, transformer: EventTransformer):
        self.transformer = transformer
    
    def process_activity_events(self, activity_id: int, athlete_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process all events for an activity across multiple athletes."""
        all_events = []
        
        for athlete_data in athlete_events:
            athlete_id = athlete_data.get("athlete_id")
            events_data = athlete_data.get("events", [])
            
            if not athlete_id:
                logger.warning("Missing athlete_id in event data")
                continue
            
            for event_data in events_data:
                transformed_events = self.transformer.transform(
                    event_data, 
                    activity_id=activity_id, 
                    athlete_id=athlete_id
                )
                all_events.extend(transformed_events)
        
        return all_events