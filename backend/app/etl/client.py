"""Catapult Sports API client."""

import httpx
import logging
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class CatapultAPIClient:
    """Async HTTP client for Catapult Sports API."""
    
    def __init__(self, api_url: str = None, headers: Dict[str, str] = None):
        self.api_url = api_url or settings.catapult_api_url
        self.headers = headers or settings.catapult_headers
        self.client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers=self.headers,
            timeout=30.0
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make GET request to API endpoint."""
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {endpoint}: {e}")
            return None
    
    async def fetch_activities(self) -> List[Dict[str, Any]]:
        """Fetch activities from the API."""
        logger.info("Fetching activities from Catapult API")
        data = await self.get("/activities")
        return data if data else []
    
    async def fetch_athletes(self, activity_id: int) -> List[Dict[str, Any]]:
        """Fetch athletes for a specific activity."""
        logger.info(f"Fetching athletes for activity {activity_id}")
        data = await self.get(f"/activities/{activity_id}/athletes")
        return data if data else []
    
    async def fetch_periods(self, activity_id: int) -> List[Dict[str, Any]]:
        """Fetch periods for a specific activity."""
        logger.info(f"Fetching periods for activity {activity_id}")
        data = await self.get(f"/activities/{activity_id}/periods")
        return data if data else []
    
    async def fetch_events(self, activity_id: int, athlete_id: int, event_types: str = None) -> List[Dict[str, Any]]:
        """Fetch events for a specific activity and athlete."""
        if not event_types:
            event_types = "ima_acceleration,ima_jump,football_movement_analysis"
        
        logger.info(f"Fetching events for activity {activity_id}, athlete {athlete_id}")
        params = {"event_types": event_types}
        data = await self.get(f"/activities/{activity_id}/athletes/{athlete_id}/events", params)
        return data if data else []
    
    async def fetch_efforts(self, activity_id: int, athlete_id: int, effort_types: str = None) -> List[Dict[str, Any]]:
        """Fetch efforts for a specific activity and athlete."""
        if not effort_types:
            effort_types = "velocity,acceleration"
        
        logger.info(f"Fetching efforts for activity {activity_id}, athlete {athlete_id}")
        params = {"effort_types": effort_types}
        data = await self.get(f"/activities/{activity_id}/athletes/{athlete_id}/efforts", params)
        return data if data else []
    
    async def fetch_positions(self) -> List[Dict[str, Any]]:
        """Fetch positions from the API."""
        logger.info("Fetching positions from Catapult API")
        data = await self.get("/positions")
        return data if data else []
    
    async def fetch_parameters(self) -> List[Dict[str, Any]]:
        """Fetch parameters from the API."""
        logger.info("Fetching parameters from Catapult API")
        data = await self.get("/parameters")
        return data if data else []


# Sync client for backward compatibility with existing code
class CatapultSyncClient:
    """Synchronous HTTP client for Catapult Sports API."""
    
    def __init__(self, api_url: str = None, headers: Dict[str, str] = None):
        self.api_url = api_url or settings.catapult_api_url
        self.headers = headers or settings.catapult_headers
    
    def get(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make GET request to API endpoint."""
        try:
            with httpx.Client(base_url=self.api_url, headers=self.headers, timeout=30.0) as client:
                response = client.get(endpoint, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {endpoint}: {e}")
            return None
    
    def fetch_activities(self) -> List[Dict[str, Any]]:
        """Fetch activities from the API."""
        logger.info("Fetching activities from Catapult API")
        data = self.get("/activities")
        return data if data else []
    
    def fetch_athletes(self, activity_id: int) -> List[Dict[str, Any]]:
        """Fetch athletes for a specific activity."""
        logger.info(f"Fetching athletes for activity {activity_id}")
        data = self.get(f"/activities/{activity_id}/athletes")
        return data if data else []
    
    def fetch_periods(self, activity_id: int) -> List[Dict[str, Any]]:
        """Fetch periods for a specific activity."""
        logger.info(f"Fetching periods for activity {activity_id}")
        data = self.get(f"/activities/{activity_id}/periods")
        return data if data else []
    
    def fetch_events(self, activity_id: int, athlete_id: int, event_types: str = None) -> List[Dict[str, Any]]:
        """Fetch events for a specific activity and athlete."""
        if not event_types:
            event_types = "ima_acceleration,ima_jump,football_movement_analysis"
        
        logger.info(f"Fetching events for activity {activity_id}, athlete {athlete_id}")
        params = {"event_types": event_types}
        data = self.get(f"/activities/{activity_id}/athletes/{athlete_id}/events", params)
        return data if data else []
    
    def fetch_efforts(self, activity_id: int, athlete_id: int, effort_types: str = None) -> List[Dict[str, Any]]:
        """Fetch efforts for a specific activity and athlete."""
        if not effort_types:
            effort_types = "velocity,acceleration"
        
        logger.info(f"Fetching efforts for activity {activity_id}, athlete {athlete_id}")
        params = {"effort_types": effort_types}
        data = self.get(f"/activities/{activity_id}/athletes/{athlete_id}/efforts", params)
        return data if data else []
    
    def fetch_positions(self) -> List[Dict[str, Any]]:
        """Fetch positions from the API."""
        logger.info("Fetching positions from Catapult API")
        data = self.get("/positions")
        return data if data else []
    
    def fetch_parameters(self) -> List[Dict[str, Any]]:
        """Fetch parameters from the API."""
        logger.info("Fetching parameters from Catapult API")
        data = self.get("/parameters")
        return data if data else []