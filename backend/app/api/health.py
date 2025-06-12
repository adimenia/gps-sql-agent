"""Health check endpoints."""

import asyncio
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from app.etl.client import CatapultAPIClient

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.app_env,
        "version": "0.1.0"
    }


@router.get("/database")
async def database_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Database connectivity health check."""
    try:
        # Test basic connectivity
        result = db.execute(text("SELECT 1")).scalar()
        if result != 1:
            raise Exception("Database query returned unexpected result")
        
        # Test database tables exist
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables_result = db.execute(tables_query).fetchall()
        tables = [row[0] for row in tables_result]
        
        # Check for required tables
        required_tables = ['activities', 'athletes', 'events', 'efforts', 'owners']
        missing_tables = [table for table in required_tables if table not in tables]
        
        status = "healthy" if not missing_tables else "degraded"
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "database_connected": True,
            "tables_found": len(tables),
            "required_tables": required_tables,
            "missing_tables": missing_tables,
            "database_url": f"postgresql://{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database_connected": False,
            "error": str(e),
            "database_url": f"postgresql://{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        }


@router.get("/api")
async def api_health() -> Dict[str, Any]:
    """Catapult API connectivity health check."""
    if not settings.catapult_api_token:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "api_configured": False,
            "error": "CATAPULT_API_TOKEN not configured"
        }
    
    try:
        async with CatapultAPIClient() as client:
            # Test API connectivity with a simple request
            activities = await client.fetch_activities()
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "api_configured": True,
                "api_accessible": True,
                "api_url": settings.catapult_api_url,
                "sample_data_available": len(activities) > 0,
                "activities_count": len(activities) if activities else 0
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "api_configured": True,
            "api_accessible": False,
            "api_url": settings.catapult_api_url,
            "error": str(e)
        }


@router.get("/etl")
async def etl_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """ETL system health check."""
    try:
        # Check for recent data
        from app.models.sports import Activity, Athlete, Event, Effort
        
        activity_count = db.query(Activity).count()
        athlete_count = db.query(Athlete).count()
        event_count = db.query(Event).count()
        effort_count = db.query(Effort).count()
        
        # Get most recent activity
        latest_activity = db.query(Activity).order_by(Activity.created_at.desc()).first()
        
        data_freshness = None
        if latest_activity and latest_activity.created_at:
            data_age = datetime.now() - latest_activity.created_at
            data_freshness = {
                "latest_activity_date": latest_activity.created_at.isoformat(),
                "data_age_hours": round(data_age.total_seconds() / 3600, 2)
            }
        
        status = "healthy" if activity_count > 0 else "degraded"
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "data_counts": {
                "activities": activity_count,
                "athletes": athlete_count,
                "events": event_count,
                "efforts": effort_count
            },
            "data_freshness": data_freshness,
            "etl_components": {
                "transformers": ["activities", "athletes", "events", "efforts"],
                "loaders": ["batch_loader", "sports_loaders"],
                "orchestrator": "available"
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/full")
async def full_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Comprehensive health check of all system components."""
    try:
        # Run all health checks in parallel
        basic_health_task = health_check()
        database_health_task = database_health(db)
        api_health_task = api_health()
        etl_health_task = etl_health(db)
        
        # Await all tasks
        basic_result = await basic_health_task
        database_result = await database_health_task
        api_result = await api_health_task
        etl_result = await etl_health_task
        
        # Determine overall status
        statuses = [
            basic_result.get("status"),
            database_result.get("status"),
            api_result.get("status"),
            etl_result.get("status")
        ]
        
        if all(status == "healthy" for status in statuses):
            overall_status = "healthy"
        elif any(status == "unhealthy" for status in statuses):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "basic": basic_result,
                "database": database_result,
                "api": api_result,
                "etl": etl_result
            },
            "summary": {
                "healthy_components": len([s for s in statuses if s == "healthy"]),
                "total_components": len(statuses),
                "issues": [
                    component for component, result in {
                        "database": database_result,
                        "api": api_result,
                        "etl": etl_result
                    }.items()
                    if result.get("status") != "healthy"
                ]
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": f"Health check system error: {str(e)}"
        }