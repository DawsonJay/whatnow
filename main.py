#!/usr/bin/env python3
"""
WhatNow FastAPI Application
Main entry point for the activity recommendation system
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.connection import get_db, engine, Base
from database.models import Activity
from database.schemas import ActivityCreate, ActivityResponse
import os

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

# Create database tables (with error handling)
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")
    print("This is expected if DATABASE_URL is not set yet")

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "WhatNow API", "status": "running"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "whatnow"}

@app.get("/db-test")
def test_database(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        # Simple query to test connection
        result = db.execute("SELECT 1 as test").fetchone()
        return {"database": "connected", "test": result[0]}
    except Exception as e:
        return {"database": "error", "error": str(e)}

# Database endpoints
@app.get("/activities", response_model=list[ActivityResponse])
def get_activities(
    category: str = None,
    energy_min: float = None,
    energy_max: float = None,
    db: Session = Depends(get_db)
):
    """Get all activities with optional filtering"""
    try:
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

@app.get("/activities/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """Get a specific activity by ID"""
    try:
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

@app.get("/activities/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all available activity categories"""
    try:
        categories = db.query(Activity.category).distinct().all()
        return [cat[0] for cat in categories if cat[0]]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch categories: {str(e)}"
        )

@app.post("/activities", response_model=ActivityResponse)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    """Create a new activity"""
    try:
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

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)