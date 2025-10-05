#!/usr/bin/env python3
"""
Activity-related endpoints for the WhatNow AI system.
"""

import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.database import get_database_session, Activity, Base, engine
# from utils.embeddings import create_activity_payload  # Removed for faster deployment

router = APIRouter(prefix="/activities", tags=["activities"])

@router.post("/init-db")
def init_database():
    """Initialize database tables with the current schema."""
    try:
        # Drop and recreate all tables
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        return {
            "message": "Database initialized successfully",
            "tables_created": ["activities"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize database: {str(e)}")

@router.delete("/clear")
def clear_activities(db: Session = Depends(get_database_session)):
    """Clear all activities from the database."""
    try:
        # Delete all activities
        db.query(Activity).delete()
        db.commit()
        
        return {
            "message": "All activities cleared successfully",
            "count": 0
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear activities: {str(e)}")

@router.post("/bulk-upload")
def bulk_upload_activities(
    request: Dict[str, Any],
    db: Session = Depends(get_database_session)
):
    """
    Bulk upload activities with pre-computed embeddings.
    
    Expected request format:
    {
        "activities": [
            {"name": "Reading", "embedding": [0.1, 0.2, 0.3, ...]},
            {"name": "Swimming", "embedding": [0.4, 0.5, 0.6, ...]}
        ]
    }
    """
    try:
        # Validate request
        if "activities" not in request:
            raise HTTPException(status_code=400, detail="Missing 'activities' field")
        
        activities = request["activities"]
        if not isinstance(activities, list):
            raise HTTPException(status_code=400, detail="'activities' must be a list")
        
        if not activities:
            return {
                "message": "No activities provided",
                "imported": 0,
                "duplicates": 0,
                "total": 0
            }
        
        # Check for duplicates
        activity_names = [activity["name"] for activity in activities]
        existing_activities = db.query(Activity).filter(Activity.name.in_(activity_names)).all()
        existing_names = {activity.name for activity in existing_activities}
        
        # Filter out duplicates
        new_activities = [activity for activity in activities if activity["name"] not in existing_names]
        
        if not new_activities:
            return {
                "message": "All activities already exist",
                "imported": 0,
                "duplicates": len(activities),
                "total": len(activities)
            }
        
        # Create database entries
        created_count = 0
        for activity_data in new_activities:
            try:
                activity = Activity(
                    name=activity_data["name"],
                    embedding=json.dumps(activity_data["embedding"])
                )
                db.add(activity)
                created_count += 1
            except Exception as e:
                print(f"Error creating activity {activity_data['name']}: {str(e)}")
                continue
        
        db.commit()
        
        return {
            "message": f"Successfully uploaded {created_count} new activities",
            "imported": created_count,
            "duplicates": len(activities) - len(new_activities),
            "total": len(activities)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload activities: {str(e)}")

@router.get("/")
def list_activities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_database_session)
):
    """List activities with pagination."""
    try:
        activities = db.query(Activity).offset(skip).limit(limit).all()
        
        return {
            "activities": [
                {
                    "id": activity.id,
                    "name": activity.name,
                    "created_at": activity.created_at.isoformat() if activity.created_at else None
                }
                for activity in activities
            ],
            "total": db.query(Activity).count(),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list activities: {str(e)}")
