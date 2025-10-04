#!/usr/bin/env python3
"""
WhatNow FastAPI Application
Main entry point for the activity recommendation system
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from dotenv import load_dotenv

from database.connection import get_db, engine
from database.models import Activity, Base
from database.schemas import ActivityCreate, ActivityResponse

# Load environment variables
load_dotenv()

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

# Create database tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "WhatNow API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "whatnow",
        "database": "connected"
    }

@app.get("/db-test")
def test_database(db: Session = Depends(get_db)):
    """Test database connection and return basic info"""
    try:
        # Test database connection
        activity_count = db.query(Activity).count()
        
        return {
            "status": "connected",
            "database": "postgresql",
            "activities_count": activity_count,
            "message": "Database connection successful"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

@app.post("/activities", response_model=ActivityResponse)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    """Create a new activity"""
    try:
        db_activity = Activity(**activity.dict())
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

@app.get("/activities", response_model=List[ActivityResponse])
def list_activities(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all activities with optional filtering"""
    try:
        query = db.query(Activity)
        
        if category:
            query = query.filter(Activity.category == category)
        
        activities = query.offset(skip).limit(limit).all()
        return activities
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch activities: {str(e)}"
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
