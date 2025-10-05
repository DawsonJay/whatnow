#!/usr/bin/env python3
"""
Activity-related endpoints for the WhatNow AI system.
"""

import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.database import get_database_session, Activity
from utils.embeddings import create_activity_payload

router = APIRouter(prefix="/activities", tags=["activities"])

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

@router.post("/import-titles")
def import_activity_titles(
    request: Dict[str, Any],
    db: Session = Depends(get_database_session)
):
    """
    Import activity titles, check for duplicates, generate embeddings, and create database entries.
    
    Expected request format:
    {
        "titles": ["Activity 1", "Activity 2", ...]
    }
    """
    try:
        # Validate request
        if "titles" not in request:
            raise HTTPException(status_code=400, detail="Missing 'titles' field in request")
        
        titles = request["titles"]
        if not isinstance(titles, list):
            raise HTTPException(status_code=400, detail="'titles' must be a list")
        
        if not titles:
            return {
                "message": "No titles provided",
                "imported": 0,
                "duplicates": 0,
                "total": 0
            }
        
        # Check for duplicates
        existing_activities = db.query(Activity).filter(Activity.name.in_(titles)).all()
        existing_names = {activity.name for activity in existing_activities}
        
        # Filter out duplicates
        new_titles = [title for title in titles if title not in existing_names]
        
        if not new_titles:
            return {
                "message": "All activities already exist",
                "imported": 0,
                "duplicates": len(titles),
                "total": len(titles)
            }
        
        # Generate embeddings for new activities
        activity_payload = create_activity_payload(new_titles)
        
        # Create database entries
        created_count = 0
        for activity_data in activity_payload:
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
            "message": f"Successfully imported {created_count} new activities",
            "imported": created_count,
            "duplicates": len(titles) - len(new_titles),
            "total": len(titles)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to import activities: {str(e)}")

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
