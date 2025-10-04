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
    category: str = None,
    energy_min: float = None,
    energy_max: float = None
):
    """Get all activities with optional filtering"""
    db = get_database_session()
    
    try:
        from database.models import Activity
        query = db.query(Activity)
        
        if category:
            query = query.filter(Activity.category == category)
        if energy_min is not None:
            query = query.filter(Activity.energy_physical >= energy_min)
        if energy_max is not None:
            query = query.filter(Activity.energy_physical <= energy_max)
            
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