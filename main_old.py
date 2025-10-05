#!/usr/bin/env python3
"""
WhatNow FastAPI Application
AI-powered activity recommendation system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

# Database imports with graceful fallback
try:
    from database.schemas import ActivityCreate, ActivityResponse
    DATABASE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import database modules: {e}")
    DATABASE_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="WhatNow API",
    description="AI-powered activity recommendation system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_database_session():
    """Get database session with error handling"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Database not available"
        )
    
    try:
        from database.connection import get_db
        return next(get_db())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

# ============================================================================
# BASIC ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "WhatNow API", "status": "running"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "whatnow"}

@app.get("/db-test")
def test_database():
    """Test database connection"""
    if not DATABASE_AVAILABLE:
        return {"database": "not_available", "error": "Database modules not imported"}
    
    try:
        from database.connection import get_db
        from sqlalchemy import text
        db = next(get_db())
        result = db.execute(text("SELECT 1 as test")).fetchone()
        return {"database": "connected", "test": result[0]}
    except Exception as e:
        return {"database": "error", "error": str(e)}

# ============================================================================
# ACTIVITY ENDPOINTS
# ============================================================================

@app.get("/activities/categories")
def get_categories():
    """Get all available activity categories"""
    db = get_database_session()
    
    try:
        from database.models import Activity
        categories = db.query(Activity.category).distinct().all()
        return [cat[0] for cat in categories if cat[0]]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch categories: {str(e)}"
        )

@app.get("/activities")
def get_activities(
    # Basic filters
    category: str = None,
    cost: str = None,
    
    # Energy filters (0-10 scale)
    energy_physical_min: float = None,
    energy_physical_max: float = None,
    energy_mental_min: float = None,
    energy_mental_max: float = None,
    social_level_min: float = None,
    social_level_max: float = None,
    
    # Duration filters (minutes)
    duration_min: int = None,
    duration_max: int = None,
    
    # Location filters
    indoor: bool = None,
    outdoor: bool = None,
    
    # Weather filters
    not_avoid_weather: str = None,  # Filter for activities that don't avoid this weather
    with_best_weather: str = None,  # Filter for activities that prefer this weather
    temperature_min: float = None,
    temperature_max: float = None,
    
    # Time filters
    time_of_day: str = None,  # morning, afternoon, evening, night
    
    # Tag filters
    tag: str = None,  # Filter by specific tag
    tags: str = None,  # Filter by multiple tags (comma-separated)
    tag_logic: str = "or",  # "and" or "or" logic for multiple tags
    
    # Search
    search: str = None  # Search in name and description
):
    """Get all activities with comprehensive filtering options"""
    db = get_database_session()
    
    try:
        from database.models import Activity
        from sqlalchemy import and_, or_
        query = db.query(Activity)
        
        # Basic filters
        if category:
            query = query.filter(Activity.category == category)
        if cost:
            query = query.filter(Activity.cost == cost)
        
        # Energy filters
        if energy_physical_min is not None:
            query = query.filter(Activity.energy_physical >= energy_physical_min)
        if energy_physical_max is not None:
            query = query.filter(Activity.energy_physical <= energy_physical_max)
        if energy_mental_min is not None:
            query = query.filter(Activity.energy_mental >= energy_mental_min)
        if energy_mental_max is not None:
            query = query.filter(Activity.energy_mental <= energy_mental_max)
        if social_level_min is not None:
            query = query.filter(Activity.social_level >= social_level_min)
        if social_level_max is not None:
            query = query.filter(Activity.social_level <= social_level_max)
        
        # Duration filters
        if duration_min is not None:
            query = query.filter(Activity.duration_min >= duration_min)
        if duration_max is not None:
            query = query.filter(Activity.duration_max <= duration_max)
        
        # Location filters
        if indoor is not None:
            query = query.filter(Activity.indoor == indoor)
        if outdoor is not None:
            query = query.filter(Activity.outdoor == outdoor)
        
        # Weather filters - Clear and explicit
        if not_avoid_weather:
            # Return activities that don't avoid this weather type
            # Use a simpler approach: filter out activities where weather_avoid contains the weather
            from sqlalchemy import text
            query = query.filter(
                text("weather_avoid::jsonb @> :weather_param IS NOT TRUE")
            ).params(weather_param=f'["{not_avoid_weather}"]')
        
        if with_best_weather:
            # Return activities that prefer this weather type
            from sqlalchemy import text
            query = query.filter(
                text("weather_best::jsonb @> :weather_param")
            ).params(weather_param=f'["{with_best_weather}"]')
        if temperature_min is not None:
            query = query.filter(Activity.temperature_min <= temperature_min)
        if temperature_max is not None:
            query = query.filter(Activity.temperature_max >= temperature_max)
        
        # Time of day filter
        if time_of_day:
            from sqlalchemy import text
            query = query.filter(text("time_of_day::jsonb @> :time_param")).params(time_param=f'["{time_of_day}"]')
        
        # Tag filters
        if tag:
            from sqlalchemy import text
            query = query.filter(text("tags::jsonb @> :tag_param")).params(tag_param=f'["{tag}"]')
        
        if tags:
            from sqlalchemy import text, or_
            tag_list = [t.strip() for t in tags.split(',')]
            if tag_logic.lower() == "and":
                # Activities must have ALL specified tags
                for tag_item in tag_list:
                    query = query.filter(text("tags::jsonb @> :tag_param")).params(tag_param=f'["{tag_item}"]')
            else:
                # Activities must have ANY of the specified tags (OR logic)
                tag_filters = [text("tags::jsonb @> :tag_param").params(tag_param=f'["{tag_item}"]') for tag_item in tag_list]
                query = query.filter(or_(*tag_filters))
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Activity.name.ilike(search_term),
                    Activity.description.ilike(search_term)
                )
            )
            
        activities = query.all()
        return activities
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch activities: {str(e)}"
        )

@app.get("/activities/{activity_id}")
def get_activity(activity_id: int):
    """Get a specific activity by ID"""
    db = get_database_session()
    
    try:
        from database.models import Activity
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            raise HTTPException(
                status_code=404,
                detail="Activity not found"
            )
        return activity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch activity: {str(e)}"
        )

@app.post("/activities")
def create_activity(activity: ActivityCreate):
    """Create a new activity"""
    db = get_database_session()
    
    try:
        from database.models import Activity
        db_activity = Activity(**activity.model_dump())
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create activity: {str(e)}"
        )

@app.delete("/activities/clear")
def clear_all_activities():
    """
    Delete all activities from the database
    CAUTION: This will permanently delete all activity data!
    """
    db = get_database_session()
    
    try:
        from database.models import Activity
        
        # Count before deletion
        count = db.query(Activity).count()
        
        # Delete all activities
        db.query(Activity).delete()
        db.commit()
        
        return {
            "message": f"Successfully deleted {count} activities",
            "deleted": count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear activities: {str(e)}"
        )

@app.post("/activities/bulk")
def bulk_import_activities(activities: List[ActivityCreate]):
    """Bulk import activities with strict validation"""
    db = get_database_session()
    
    try:
        from database.models import Activity
        
        # Check for duplicates by name
        existing_names = {name[0] for name in db.query(Activity.name).all()}
        new_names = {activity.name for activity in activities}
        
        duplicates = existing_names.intersection(new_names)
        if duplicates:
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate activities found: {list(duplicates)}"
            )
        
        # Validate all activities pass schema validation
        validated_activities = []
        for activity in activities:
            try:
                validated_activity = Activity(**activity.model_dump())
                validated_activities.append(validated_activity)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid activity data: {str(e)}"
                )
        
        # Add all activities in a transaction
        db.add_all(validated_activities)
        db.commit()
        
        return {
            "message": f"Successfully imported {len(validated_activities)} activities",
            "count": len(validated_activities)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Bulk import failed: {str(e)}"
        )

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)