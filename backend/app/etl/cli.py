#!/usr/bin/env python3
"""CLI runner for the ETL pipeline."""

import asyncio
import argparse
import logging
import sys
from datetime import datetime
from app.etl.orchestrator import run_etl_pipeline
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def run_full_pipeline():
    """Run the complete ETL pipeline."""
    logger.info("Starting ETL pipeline execution")
    start_time = datetime.now()
    
    try:
        stats = await run_etl_pipeline()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "="*50)
        print("ETL Pipeline Completed Successfully!")
        print("="*50)
        print(f"Duration: {duration}")
        print(f"Start Time: {start_time}")
        print(f"End Time: {end_time}")
        print("\nRecords Processed:")
        for data_type, count in stats.items():
            print(f"  {data_type.capitalize()}: {count}")
        print("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        print(f"\n❌ ETL Pipeline Failed: {e}")
        return False


async def test_api_connection():
    """Test connection to Catapult API."""
    from app.etl.client import CatapultAPIClient
    
    logger.info("Testing API connection")
    
    try:
        async with CatapultAPIClient() as client:
            activities = await client.fetch_activities()
            
            if activities:
                print(f"✅ API Connection Successful! Found {len(activities)} activities.")
                return True
            else:
                print("⚠️  API Connection Successful but no activities found.")
                return True
                
    except Exception as e:
        logger.error(f"API connection test failed: {e}")
        print(f"❌ API Connection Failed: {e}")
        return False


async def run_dry_run():
    """Run a dry run of the ETL pipeline (extract and transform only)."""
    from app.etl.client import CatapultAPIClient
    from app.etl.transformers import ActivityTransformer, AthleteTransformer
    
    logger.info("Running ETL dry run")
    
    try:
        async with CatapultAPIClient() as client:
            # Test activity extraction and transformation
            raw_activities = await client.fetch_activities()
            
            activity_transformer = ActivityTransformer()
            transformed_activities = []
            
            for raw_activity in raw_activities[:5]:  # Limit to 5 for dry run
                transformed = activity_transformer.transform(raw_activity)
                transformed_activities.extend(transformed)
            
            print(f"✅ Dry Run Successful!")
            print(f"   - Extracted {len(raw_activities)} activities")
            print(f"   - Transformed {len(transformed_activities)} activity records")
            
            if transformed_activities:
                print(f"   - Sample transformed activity: {transformed_activities[0]['name']}")
            
            return True
            
    except Exception as e:
        logger.error(f"Dry run failed: {e}")
        print(f"❌ Dry Run Failed: {e}")
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Sports Analytics ETL Pipeline")
    parser.add_argument(
        "command", 
        choices=["run", "test", "dry-run"],
        help="Command to execute"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Remove logs directory requirement since we use stdout only
    
    print("🏃‍♂️ Sports Analytics ETL Pipeline")
    print("="*40)
    
    # Validate configuration
    if not settings.catapult_api_token:
        print("❌ Error: CATAPULT_API_TOKEN not configured")
        print("Please set the CATAPULT_API_TOKEN environment variable")
        sys.exit(1)
    
    if not settings.postgres_host:
        print("❌ Error: Database configuration missing")
        print("Please configure database connection settings")
        sys.exit(1)
    
    # Run the appropriate command
    success = False
    
    if args.command == "test":
        success = asyncio.run(test_api_connection())
    elif args.command == "dry-run":
        success = asyncio.run(run_dry_run())
    elif args.command == "run":
        success = asyncio.run(run_full_pipeline())
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()