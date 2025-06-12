"""API endpoints for periods and activities."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models.sports import Activity, Period, Athlete

router = APIRouter(prefix="/periods", tags=["periods"])


# Pydantic models for request/response
class PeriodResponse(BaseModel):
    period_id: int
    activity_id: int
    name: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    is_deleted: bool

    class Config:
        from_attributes = True


class ActivityResponse(BaseModel):
    activity_id: int
    name: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    game_id: Optional[int]
    owner_id: Optional[int]
    owner_name: Optional[str]
    athlete_count: Optional[int]
    period_count: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ActivityWithPeriodsResponse(ActivityResponse):
    periods: List[PeriodResponse] = []


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


@router.get("/activities", response_model=PaginatedResponse)
async def get_activities(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    sort_by: str = Query("activity_id", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    name_filter: Optional[str] = Query(None, description="Filter by activity name"),
    owner_filter: Optional[str] = Query(None, description="Filter by owner name"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (from)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (to)"),
    db: Session = Depends(get_db)
) -> PaginatedResponse:
    """Get paginated list of activities with filtering and sorting."""
    
    # Build query
    query = db.query(Activity)
    
    # Apply filters
    if name_filter:
        query = query.filter(Activity.name.ilike(f"%{name_filter}%"))
    
    if owner_filter:
        query = query.filter(Activity.owner_name.ilike(f"%{owner_filter}%"))
    
    if start_date:
        query = query.filter(Activity.start_time >= start_date)
    
    if end_date:
        query = query.filter(Activity.start_time <= end_date)
    
    # Apply sorting
    sort_column = getattr(Activity, sort_by, Activity.activity_id)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    activities = query.offset(offset).limit(size).all()
    
    # Calculate pagination info
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[ActivityResponse.from_orm(activity) for activity in activities],
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/activities/{activity_id}", response_model=ActivityWithPeriodsResponse)
async def get_activity(
    activity_id: int,
    include_periods: bool = Query(True, description="Include periods in response"),
    db: Session = Depends(get_db)
) -> ActivityWithPeriodsResponse:
    """Get a specific activity by ID with optional periods."""
    
    activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    response = ActivityWithPeriodsResponse.from_orm(activity)
    
    if include_periods:
        periods = db.query(Period).filter(
            Period.activity_id == activity_id,
            Period.is_deleted == False
        ).all()
        response.periods = [PeriodResponse.from_orm(period) for period in periods]
    
    return response


@router.get("/activities/{activity_id}/periods", response_model=List[PeriodResponse])
async def get_activity_periods(
    activity_id: int,
    db: Session = Depends(get_db)
) -> List[PeriodResponse]:
    """Get all periods for a specific activity."""
    
    # Verify activity exists
    activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    periods = db.query(Period).filter(
        Period.activity_id == activity_id,
        Period.is_deleted == False
    ).order_by(Period.start_time).all()
    
    return [PeriodResponse.from_orm(period) for period in periods]


@router.get("/", response_model=PaginatedResponse)
async def get_periods(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    sort_by: str = Query("period_id", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    activity_id: Optional[int] = Query(None, description="Filter by activity ID"),
    name_filter: Optional[str] = Query(None, description="Filter by period name"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (from)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (to)"),
    db: Session = Depends(get_db)
) -> PaginatedResponse:
    """Get paginated list of periods with filtering and sorting."""
    
    # Build query
    query = db.query(Period).filter(Period.is_deleted == False)
    
    # Apply filters
    if activity_id:
        query = query.filter(Period.activity_id == activity_id)
    
    if name_filter:
        query = query.filter(Period.name.ilike(f"%{name_filter}%"))
    
    if start_date:
        query = query.filter(Period.start_time >= start_date)
    
    if end_date:
        query = query.filter(Period.start_time <= end_date)
    
    # Apply sorting
    sort_column = getattr(Period, sort_by, Period.period_id)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    periods = query.offset(offset).limit(size).all()
    
    # Calculate pagination info
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[PeriodResponse.from_orm(period) for period in periods],
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{period_id}", response_model=PeriodResponse)
async def get_period(
    period_id: int,
    db: Session = Depends(get_db)
) -> PeriodResponse:
    """Get a specific period by ID."""
    
    period = db.query(Period).filter(
        Period.period_id == period_id,
        Period.is_deleted == False
    ).first()
    
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    
    return PeriodResponse.from_orm(period)


@router.get("/stats/summary")
async def get_periods_stats(
    activity_id: Optional[int] = Query(None, description="Filter by activity ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (from)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (to)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get summary statistics for periods and activities."""
    
    # Activities stats
    activities_query = db.query(Activity)
    if start_date:
        activities_query = activities_query.filter(Activity.start_time >= start_date)
    if end_date:
        activities_query = activities_query.filter(Activity.start_time <= end_date)
    
    total_activities = activities_query.count()
    
    # Periods stats
    periods_query = db.query(Period).filter(Period.is_deleted == False)
    if activity_id:
        periods_query = periods_query.filter(Period.activity_id == activity_id)
    if start_date:
        periods_query = periods_query.filter(Period.start_time >= start_date)
    if end_date:
        periods_query = periods_query.filter(Period.start_time <= end_date)
    
    total_periods = periods_query.count()
    
    # Athletes involved
    athletes_query = db.query(Athlete)
    total_athletes = athletes_query.count()
    
    # Recent activity
    latest_activity = db.query(Activity).order_by(desc(Activity.created_at)).first()
    latest_period = db.query(Period).filter(Period.is_deleted == False).order_by(desc(Period.created_at)).first()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_activities": total_activities,
            "total_periods": total_periods,
            "total_athletes": total_athletes
        },
        "latest_data": {
            "latest_activity_id": latest_activity.activity_id if latest_activity else None,
            "latest_activity_date": latest_activity.created_at.isoformat() if latest_activity and latest_activity.created_at else None,
            "latest_period_id": latest_period.period_id if latest_period else None,
            "latest_period_date": latest_period.created_at.isoformat() if latest_period and latest_period.created_at else None
        },
        "filters_applied": {
            "activity_id": activity_id,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    }