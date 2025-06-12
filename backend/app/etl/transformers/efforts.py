"""Effort data transformer."""

from typing import Dict, List, Any
from .base import BaseTransformer
import logging

logger = logging.getLogger(__name__)


class EffortTransformer(BaseTransformer):
    """Transform raw effort data for database insertion."""
    
    def transform(self, raw_effort: Dict[str, Any], activity_id: int = None, athlete_id: int = None) -> List[Dict[str, Any]]:
        """Transform effort data from API response."""
        if not activity_id or not athlete_id:
            logger.error("activity_id and athlete_id are required for effort transformation")
            return []
        
        transformed_efforts = []
        device_id = raw_effort.get("device_id")
        effort_data = raw_effort.get("data", {})
        
        if not isinstance(effort_data, dict):
            logger.error(f"Invalid effort data format: {effort_data}")
            return []
        
        # Process velocity efforts
        velocity_efforts = effort_data.get("velocity_efforts", [])
        for effort in velocity_efforts:
            try:
                transformed = {
                    "athlete_id": athlete_id,
                    "activity_id": activity_id,
                    "device_id": device_id,
                    "start_time": self.transform_timestamp(effort.get("start_time")),
                    "end_time": self.transform_timestamp(effort.get("end_time")),
                    "band": self.safe_get(effort, "band"),
                    "distance": self.safe_float(effort.get("distance")),
                    "velocity": self.safe_float(effort.get("max_velocity")),
                    "acceleration": None  # Velocity efforts don't have acceleration
                }
                
                transformed_efforts.append(transformed)
                logger.debug(f"Transformed velocity effort for activity {activity_id}, athlete {athlete_id}")
                
            except Exception as e:
                logger.error(f"Error transforming velocity effort: {e}")
                continue
        
        # Process acceleration efforts
        acceleration_efforts = effort_data.get("acceleration_efforts", [])
        for effort in acceleration_efforts:
            try:
                transformed = {
                    "athlete_id": athlete_id,
                    "activity_id": activity_id,
                    "device_id": device_id,
                    "start_time": self.transform_timestamp(effort.get("start_time")),
                    "end_time": self.transform_timestamp(effort.get("end_time")),
                    "band": self.safe_get(effort, "band"),
                    "distance": self.safe_float(effort.get("distance")),
                    "velocity": None,  # Acceleration efforts don't have velocity
                    "acceleration": self.safe_float(effort.get("acceleration"))
                }
                
                transformed_efforts.append(transformed)
                logger.debug(f"Transformed acceleration effort for activity {activity_id}, athlete {athlete_id}")
                
            except Exception as e:
                logger.error(f"Error transforming acceleration effort: {e}")
                continue
        
        return transformed_efforts


class EffortAggregator:
    """Aggregate effort data for analysis."""
    
    @staticmethod
    def calculate_effort_summary(efforts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for efforts."""
        if not efforts:
            return {}
        
        velocity_efforts = [e for e in efforts if e.get("velocity") is not None]
        acceleration_efforts = [e for e in efforts if e.get("acceleration") is not None]
        
        summary = {
            "total_efforts": len(efforts),
            "velocity_efforts_count": len(velocity_efforts),
            "acceleration_efforts_count": len(acceleration_efforts),
            "total_distance": sum(e.get("distance", 0) for e in efforts if e.get("distance")),
        }
        
        if velocity_efforts:
            velocities = [e["velocity"] for e in velocity_efforts if e.get("velocity")]
            if velocities:
                summary.update({
                    "max_velocity": max(velocities),
                    "avg_velocity": sum(velocities) / len(velocities)
                })
        
        if acceleration_efforts:
            accelerations = [e["acceleration"] for e in acceleration_efforts if e.get("acceleration")]
            if accelerations:
                summary.update({
                    "max_acceleration": max(accelerations),
                    "avg_acceleration": sum(accelerations) / len(accelerations)
                })
        
        return summary