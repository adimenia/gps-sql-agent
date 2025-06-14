"""Activity data transformer."""

from typing import Dict, List, Any, Optional
from .base import BaseTransformer
import logging
import hashlib

logger = logging.getLogger(__name__)


class ActivityTransformer(BaseTransformer):
    """Transform raw activity data for database insertion."""
    
    def _convert_id_to_int(self, id_value: Any) -> Optional[int]:
        """Convert ID to integer, handling both integers and UUID strings."""
        if id_value is None:
            return None
        if isinstance(id_value, int):
            return id_value
        # Convert UUID string to integer using hash
        return abs(int(hashlib.sha256(str(id_value).encode()).hexdigest()[:15], 16))
    
    def transform(self, raw_activity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform a single activity record."""
        if not self.validate_required_fields(raw_activity, ["id", "name"]):
            return []
        
        try:
            owner_data = raw_activity.get("owner", {})
            
            # Handle both integer IDs and UUID strings
            activity_id = self._convert_id_to_int(raw_activity["id"])
            
            # Convert game_id UUID to integer if present
            game_id = self.safe_get(raw_activity, "game_id")
            if game_id:
                game_id = abs(int(hashlib.sha256(str(game_id).encode()).hexdigest()[:15], 16))
            
            transformed = {
                "activity_id": activity_id,
                "name": raw_activity["name"],
                "start_time": self.transform_timestamp(raw_activity.get("start_time")),
                "end_time": self.transform_timestamp(raw_activity.get("end_time")),
                "game_id": game_id,
                
                # Owner information (handle both integer IDs and UUID strings)
                "owner_id": self._convert_id_to_int(self.safe_get(owner_data, "id")),
                "owner_customer_id": self.safe_get(owner_data, "customer_id"),
                "owner_name": self.safe_get(owner_data, "name"),
                "owner_email": self.safe_get(owner_data, "email"),
                "owner_is_synced": self.safe_bool(owner_data.get("is_synced")),
                "owner_is_deleted": self.safe_bool(owner_data.get("is_deleted")),
                "owner_created_at": self.safe_get(owner_data, "created_at"),
                "owner_modified_at": self.safe_get(owner_data, "modified_at"),
                "owner_default": self.safe_bool(owner_data.get("default")),
                "owner_software_version": self.safe_json_dumps(owner_data.get("software_version")),
                
                # Activity metadata
                "periods": self.safe_json_dumps(raw_activity.get("periods")),
                "tags": self.safe_json_dumps(raw_activity.get("tags")),
                "tag_list": self.safe_json_dumps(raw_activity.get("tag_list")),
                "athlete_count": self.safe_int(raw_activity.get("athlete_count", 0)),
                "period_count": self.safe_int(raw_activity.get("period_count", 0)),
                "activity_athletes": self.safe_json_dumps(raw_activity.get("activity_athletes"))
            }
            
            logger.debug(f"Transformed activity {raw_activity['id']}: {raw_activity['name']}")
            return [transformed]
            
        except Exception as e:
            logger.error(f"Error transforming activity {raw_activity.get('id')}: {e}")
            return []


class OwnerExtractor:
    """Extract unique owners from activities for separate storage."""
    
    @staticmethod
    def _convert_id_to_int(id_value: Any) -> Optional[int]:
        """Convert ID to integer, handling both integers and UUID strings."""
        if id_value is None:
            return None
        if isinstance(id_value, int):
            return id_value
        # Convert UUID string to integer using hash
        return abs(int(hashlib.sha256(str(id_value).encode()).hexdigest()[:15], 16))
    
    @classmethod
    def extract_owners(cls, activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract unique owners from activity data."""
        owners_map = {}
        
        for activity in activities:
            owner_data = activity.get("owner", {})
            owner_uuid = owner_data.get("id")
            
            if owner_uuid and owner_uuid not in owners_map:
                # Convert ID using same method as ActivityTransformer
                owner_id = cls._convert_id_to_int(owner_uuid)
                
                owners_map[owner_uuid] = {
                    "owner_id": owner_id,
                    "name": owner_data.get("name"),
                    "email": owner_data.get("email"),
                    "customer_id": owner_data.get("customer_id"),
                    "default_flag": owner_data.get("default", False),
                    "is_synced": owner_data.get("is_synced", False),
                    "created_at": owner_data.get("created_at"),
                    "modified_at": owner_data.get("modified_at"),
                    "software_version": owner_data.get("software_version", {})
                }
        
        return list(owners_map.values())