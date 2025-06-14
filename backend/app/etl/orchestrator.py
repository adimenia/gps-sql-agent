"""ETL orchestrator for coordinating the complete pipeline."""

import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.etl.client import CatapultAPIClient
from app.etl.transformers.activities import ActivityTransformer, OwnerExtractor
from app.etl.transformers.athletes import AthleteTransformer
from app.etl.transformers.events import EventTransformer
from app.etl.transformers.efforts import EffortTransformer
from app.etl.loaders.sports_loaders import LoaderFactory
from app.etl.loaders.base import BatchLoader
import logging
import hashlib

logger = logging.getLogger(__name__)


class ETLOrchestrator:
    """Main ETL orchestrator for the sports analytics pipeline."""
    
    def __init__(self, db_session: Session = None):
        self.db = db_session or SessionLocal()
        self.batch_loader = BatchLoader(batch_size=100)
        
        # Initialize transformers
        self.activity_transformer = ActivityTransformer()
        self.athlete_transformer = AthleteTransformer()
        self.event_transformer = EventTransformer()
        self.effort_transformer = EffortTransformer()
        
        # Maintain mapping of original UUIDs to integer IDs for API calls
        self.activity_uuid_to_int = {}
        self.athlete_uuid_to_int = {}
    
    async def run_full_pipeline(self) -> Dict[str, int]:
        """Run the complete ETL pipeline."""
        logger.info("Starting full ETL pipeline")
        stats = {
            'activities': 0,
            'owners': 0,
            'athletes': 0,
            'events': 0,
            'efforts': 0
        }
        
        try:
            async with CatapultAPIClient() as client:
                # Step 1: Process activities and owners
                activities_stats = await self.process_activities(client)
                stats.update(activities_stats)
                
                # Step 2: Process athletes, events, and efforts for each activity
                activity_uuids = await self.get_activity_uuids()
                
                # Limit to first 3 activities for initial testing
                activity_uuids = activity_uuids[:3]
                logger.info(f"Processing {len(activity_uuids)} activities (limited for testing)")
                
                for activity_uuid in activity_uuids:
                    activity_id = self._convert_id_to_int(activity_uuid)
                    logger.info(f"Processing activity {activity_id} (UUID: {activity_uuid})")
                    
                    # Store mapping for API calls
                    self.activity_uuid_to_int[activity_uuid] = activity_id
                    
                    # Process athletes for this activity
                    athlete_stats = await self.process_activity_athletes(client, activity_uuid, activity_id)
                    stats['athletes'] += athlete_stats.get('athletes', 0)
                    
                    # Get athletes for this activity to process their events/efforts
                    athlete_data = await self.get_activity_athlete_data(client, activity_uuid)
                    
                    for athlete_uuid, athlete_id in athlete_data:
                        # Process events
                        event_stats = await self.process_athlete_events(client, activity_uuid, activity_id, athlete_uuid, athlete_id)
                        stats['events'] += event_stats.get('events', 0)
                        
                        # Process efforts
                        effort_stats = await self.process_athlete_efforts(client, activity_uuid, activity_id, athlete_uuid, athlete_id)
                        stats['efforts'] += effort_stats.get('efforts', 0)
                
                logger.info(f"ETL pipeline completed. Stats: {stats}")
                return stats
                
        except Exception as e:
            logger.error(f"Error in ETL pipeline: {e}")
            raise
        finally:
            self.db.close()
    
    async def process_activities(self, client: CatapultAPIClient) -> Dict[str, int]:
        """Process activities and extract owners."""
        logger.info("Processing activities")
        
        # Fetch activities
        raw_activities = await client.fetch_activities()
        if not raw_activities:
            logger.warning("No activities found")
            return {'activities': 0, 'owners': 0}
        
        # Transform activities
        all_activities = []
        for raw_activity in raw_activities:
            transformed = self.activity_transformer.transform(raw_activity)
            all_activities.extend(transformed)
        
        # Extract and load owners FIRST (before activities that reference them)
        owners = OwnerExtractor.extract_owners(raw_activities)
        owner_loader = LoaderFactory.get_loader('owners', self.db)
        owners_count = self.batch_loader.load_in_batches(owner_loader, owners)
        
        # Load activities AFTER owners are in place
        activity_loader = LoaderFactory.get_loader('activities', self.db)
        activities_count = self.batch_loader.load_in_batches(activity_loader, all_activities)
        
        return {'activities': activities_count, 'owners': owners_count}
    
    async def process_activity_athletes(self, client: CatapultAPIClient, activity_uuid: str, activity_id: int) -> Dict[str, int]:
        """Process athletes for a specific activity."""
        logger.info(f"Processing athletes for activity {activity_id} (UUID: {activity_uuid})")
        
        # Fetch athletes using the original UUID
        raw_athletes = await client.fetch_athletes(activity_uuid)
        if not raw_athletes:
            logger.warning(f"No athletes found for activity {activity_uuid}")
            return {'athletes': 0}
        
        # Transform athletes and store UUID mapping
        all_athletes = []
        for raw_athlete in raw_athletes:
            athlete_uuid = raw_athlete.get('id')
            if athlete_uuid:
                athlete_id = self._convert_id_to_int(athlete_uuid)
                self.athlete_uuid_to_int[athlete_uuid] = athlete_id
            
            transformed = self.athlete_transformer.transform(raw_athlete)
            all_athletes.extend(transformed)
        
        # Load athletes
        athlete_loader = LoaderFactory.get_loader('athletes', self.db)
        athletes_count = self.batch_loader.load_in_batches(athlete_loader, all_athletes)
        
        return {'athletes': athletes_count}
    
    async def process_athlete_events(self, client: CatapultAPIClient, activity_uuid: str, activity_id: int, athlete_uuid: str, athlete_id: int) -> Dict[str, int]:
        """Process events for a specific athlete in an activity."""
        logger.debug(f"Processing events for activity {activity_id}, athlete {athlete_id}")
        
        # Fetch events using original UUIDs
        raw_events = await client.fetch_events(activity_uuid, athlete_uuid)
        if not raw_events:
            return {'events': 0}
        
        # Transform events using converted integer IDs
        all_events = []
        for raw_event in raw_events:
            transformed = self.event_transformer.transform(raw_event, activity_id, athlete_id)
            all_events.extend(transformed)
        
        # Load events
        if all_events:
            event_loader = LoaderFactory.get_loader('events', self.db)
            events_count = self.batch_loader.load_in_batches(event_loader, all_events)
            return {'events': events_count}
        
        return {'events': 0}
    
    async def process_athlete_efforts(self, client: CatapultAPIClient, activity_uuid: str, activity_id: int, athlete_uuid: str, athlete_id: int) -> Dict[str, int]:
        """Process efforts for a specific athlete in an activity."""
        logger.debug(f"Processing efforts for activity {activity_id}, athlete {athlete_id}")
        
        # Fetch efforts using original UUIDs
        raw_efforts = await client.fetch_efforts(activity_uuid, athlete_uuid)
        if not raw_efforts:
            return {'efforts': 0}
        
        # Transform efforts using converted integer IDs
        all_efforts = []
        for raw_effort in raw_efforts:
            transformed = self.effort_transformer.transform(raw_effort, activity_id, athlete_id)
            all_efforts.extend(transformed)
        
        # Load efforts
        if all_efforts:
            effort_loader = LoaderFactory.get_loader('efforts', self.db)
            efforts_count = self.batch_loader.load_in_batches(effort_loader, all_efforts)
            return {'efforts': efforts_count}
        
        return {'efforts': 0}
    
    async def get_activity_uuids(self) -> List[str]:
        """Get list of activity UUIDs from API."""
        try:
            async with CatapultAPIClient() as client:
                activities = await client.fetch_activities()
                return [activity['id'] for activity in activities if 'id' in activity]
        except Exception as e:
            logger.error(f"Error fetching activity UUIDs: {e}")
            return []
    
    async def get_activity_athlete_data(self, client: CatapultAPIClient, activity_uuid: str) -> List[tuple]:
        """Get list of (athlete_uuid, athlete_id) tuples for a specific activity."""
        try:
            athletes = await client.fetch_athletes(activity_uuid)
            athlete_data = []
            for athlete in athletes:
                if 'id' in athlete:
                    athlete_uuid = athlete['id']
                    athlete_id = self._convert_id_to_int(athlete_uuid)
                    athlete_data.append((athlete_uuid, athlete_id))
            return athlete_data
        except Exception as e:
            logger.error(f"Error fetching athlete data for activity {activity_uuid}: {e}")
            return []
    
    def _convert_id_to_int(self, id_value: Any) -> Optional[int]:
        """Convert ID to integer, handling both integers and UUID strings."""
        if id_value is None:
            return None
        if isinstance(id_value, int):
            return id_value
        # Convert UUID string to integer using hash
        return abs(int(hashlib.sha256(str(id_value).encode()).hexdigest()[:15], 16))
    
    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()


# Convenience function for running the ETL pipeline
async def run_etl_pipeline() -> Dict[str, int]:
    """Run the complete ETL pipeline."""
    orchestrator = ETLOrchestrator()
    try:
        return await orchestrator.run_full_pipeline()
    finally:
        orchestrator.close()


# Sync version for backward compatibility
def run_etl_pipeline_sync() -> Dict[str, int]:
    """Run the ETL pipeline synchronously."""
    return asyncio.run(run_etl_pipeline())