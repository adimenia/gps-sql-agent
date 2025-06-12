"""Athlete data transformer."""

from typing import Dict, List, Any
from datetime import datetime
from .base import BaseTransformer
import logging

logger = logging.getLogger(__name__)


class AthleteTransformer(BaseTransformer):
    """Transform raw athlete data for database insertion."""
    
    def transform(self, raw_athlete: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform a single athlete record."""
        if not self.validate_required_fields(raw_athlete, ["id"]):
            return []
        
        try:
            # Handle date of birth conversion
            date_of_birth = self._transform_date_of_birth(raw_athlete)
            
            transformed = {
                "athlete_id": raw_athlete["id"],
                "first_name": self.safe_get(raw_athlete, "first_name"),
                "last_name": self.safe_get(raw_athlete, "last_name"),
                "gender": self.safe_get(raw_athlete, "gender"),
                "jersey_number": self.safe_int(raw_athlete.get("jersey")),
                "height": self.safe_float(raw_athlete.get("height")),
                "weight": self.safe_float(raw_athlete.get("weight")),
                "position_id": self.safe_int(raw_athlete.get("position_id")),
                "date_of_birth": date_of_birth,
                "velocity_max": self.safe_float(raw_athlete.get("velocity_max")),
                "acceleration_max": self.safe_float(raw_athlete.get("acceleration_max")),
                "heart_rate_max": self.safe_int(raw_athlete.get("heart_rate_max"))
            }
            
            logger.debug(f"Transformed athlete {raw_athlete['id']}: {raw_athlete.get('first_name', '')} {raw_athlete.get('last_name', '')}")
            return [transformed]
            
        except Exception as e:
            logger.error(f"Error transforming athlete {raw_athlete.get('id')}: {e}")
            return []
    
    def _transform_date_of_birth(self, raw_athlete: Dict[str, Any]) -> str:
        """Transform date of birth from various formats to YYYY-MM-DD string."""
        # Try date_of_birth_date first (string format)
        date_str = raw_athlete.get("date_of_birth_date")
        if date_str:
            try:
                # Validate the date format
                datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except ValueError:
                logger.warning(f"Invalid date format: {date_str}")
        
        # Try date_of_birth (Unix timestamp)
        timestamp = raw_athlete.get("date_of_birth")
        if timestamp:
            try:
                if isinstance(timestamp, int):
                    dt = datetime.utcfromtimestamp(timestamp)
                    return dt.strftime('%Y-%m-%d')
            except (ValueError, OverflowError) as e:
                logger.warning(f"Invalid timestamp for date_of_birth: {timestamp}, {e}")
        
        return None


class AthleteActivityLinker:
    """Link athletes to activities for relationship management."""
    
    @staticmethod
    def extract_athlete_activity_links(activity_data: Dict[str, Any]) -> List[Dict[str, int]]:
        """Extract athlete-activity relationships."""
        activity_id = activity_data.get("id")
        athlete_ids = activity_data.get("activity_athletes", [])
        
        links = []
        if activity_id and athlete_ids:
            for athlete_id in athlete_ids:
                try:
                    athlete_id_int = int(athlete_id)
                    links.append({
                        "activity_id": activity_id,
                        "athlete_id": athlete_id_int
                    })
                except (ValueError, TypeError):
                    logger.warning(f"Invalid athlete_id: {athlete_id}")
        
        return links