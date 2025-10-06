#!/usr/bin/env python3
"""
Activity-related endpoints for the WhatNow AI system.
"""

import json
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from utils.database import get_database_session, Activity, Base, engine
from utils.base_ai import BaseAI, encode_context
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
            "tables_created": ["activities", "ai_models"]
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

@router.post("/game/start")
def start_game(
    context_tags: List[str],
    db: Session = Depends(get_database_session)
):
    """
    Start a new recommendation session.
    
    Args:
        context_tags: List of selected context tags (e.g., ["arty", "indoor", "evening"])
        
    Returns:
        Session ID and top 100 activity recommendations
    """
    try:
        # Validate context tags
        if len(context_tags) < 3:
            raise HTTPException(status_code=400, detail="Please select at least 3 context tags")
        
        if len(context_tags) > 8:
            raise HTTPException(status_code=400, detail="Please select no more than 8 context tags")
        
        # Encode context to vector
        context_vector = encode_context(context_tags)
        
        # Get all activities with embeddings
        activities = db.query(Activity).all()
        
        if not activities:
            raise HTTPException(status_code=404, detail="No activities found in database")
        
        # Initialize Base AI
        base_ai = BaseAI()
        base_ai.load_model(db)  # Load existing model if available
        
        # Convert activities to format expected by AI
        activity_list = []
        for activity in activities:
            activity_list.append({
                "id": activity.id,
                "name": activity.name,
                "embedding": activity.embedding
            })
        
        # Get AI recommendations
        recommendations = base_ai.get_recommendations(context_vector, activity_list, top_k=100)
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        return {
            "session_id": session_id,
            "recommendations": [
                {
                    "id": activity["id"],
                    "name": activity["name"]
                }
                for activity in recommendations
            ],
            "context_tags": context_tags,
            "total_recommendations": len(recommendations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start game: {str(e)}")

@router.post("/game/train")
def train_ai(
    request: Dict[str, Any],
    db: Session = Depends(get_database_session)
):
    """
    Train the AI based on user's choice.
    
    Args:
        session_id: Session ID from start_game
        chosen_activity_id: ID of the activity the user chose
        context_tags: Context tags used in the session
        
    Returns:
        Training confirmation
    """
    try:
        # Extract parameters from request
        session_id = request.get("session_id")
        chosen_activity_id = request.get("chosen_activity_id")
        context_tags = request.get("context_tags", [])
        
        # Validate inputs
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        if not chosen_activity_id:
            raise HTTPException(status_code=400, detail="Chosen activity ID is required")
        
        if not context_tags:
            raise HTTPException(status_code=400, detail="Context tags are required")
        
        # Get the chosen activity
        chosen_activity = db.query(Activity).filter(Activity.id == chosen_activity_id).first()
        
        if not chosen_activity:
            raise HTTPException(status_code=404, detail="Chosen activity not found")
        
        # Encode context to vector
        context_vector = encode_context(context_tags)
        
        # Initialize Base AI
        base_ai = BaseAI()
        base_ai.load_model(db)  # Load existing model if available
        
        # Train the model
        print(f"Training AI with context: {context_tags}")
        print(f"Context vector shape: {context_vector.shape}")
        print(f"Chosen activity: {chosen_activity.name}")
        
        success = base_ai.train(context_vector, {
            "id": chosen_activity.id,
            "name": chosen_activity.name,
            "embedding": chosen_activity.embedding
        }, reward=1.0)
        
        if not success:
            print("AI training failed - check logs for details")
            raise HTTPException(status_code=500, detail="Failed to train AI model")
        
        # Save updated model
        if not base_ai.save_model(db):
            raise HTTPException(status_code=500, detail="Failed to save AI model")
        
        return {
            "message": "AI model updated successfully",
            "session_id": session_id,
            "chosen_activity": {
                "id": chosen_activity.id,
                "name": chosen_activity.name
            },
            "context_tags": context_tags
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to train AI: {str(e)}")
